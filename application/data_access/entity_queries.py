import logging
import sentry_sdk

from typing import Optional, List, Tuple
from sqlalchemy import select, func, or_, and_, not_, tuple_, union_all, true
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from application.core.models import EntityModel, entity_factory
from application.core.utils import log_slow_execution
from application.data_access.entity_query_helpers import (
    get_date_field_to_filter,
    get_date_to_filter,
    get_operator,
    get_point,
    has_location_filters,
    get_spatial_function_for_relation,
    normalised_params,
)
from application.db.models import EntityOrm, OldEntityOrm, EntitySubdividedOrm
from application.search.enum import GeometryRelation, PeriodOption, SuffixEntity
from application.db.session import redis_cache, DbSession, get_context_session
from application.settings import get_settings
from sqlalchemy.types import Date
from sqlalchemy.sql.expression import cast
from sqlalchemy.orm import aliased

logger = logging.getLogger(__name__)
complex_datasets = ["flood-risk-zone"]
ENTITY_SEARCH_COUNT_CAP = 10_000
PG_QUERY_CANCELED = "57014"


class EntitySearchTooBroad(Exception):
    """An entity search hit the search statement timeout."""


def record_search_too_broad(extension_tag, dataset_filters):
    """Report a too-broad search as a metric and a warning, not a Sentry error."""
    sentry_sdk.metrics.count(
        "entity.search.error",
        1,
        attributes={
            "error": "statement_timeout",
            "extension": extension_tag,
            "dataset": ",".join(dataset_filters) if dataset_filters else "all",
        },
    )
    logger.warning(
        "Entity search too broad: hit the search statement timeout",
        extra={"extension": extension_tag, "dataset_filters": dataset_filters},
    )


def get_entity_query(
    id: int,
) -> Tuple[Optional[EntityModel], Optional[int], Optional[int]]:
    with get_context_session() as session:
        old_entity = (
            session.query(OldEntityOrm)
            .filter(OldEntityOrm.old_entity_id == id)
            .one_or_none()
        )
        if old_entity:
            return (
                None,
                old_entity.status,
                old_entity.new_entity_id,
            )

        entity = session.get(EntityOrm, id)
        if not entity:
            return None, None, None
        else:
            return entity_factory(entity), None, None


def get_entity_count(
    session: Session,
    datasets: Optional[List[str]] = None,
):
    sql = select(EntityOrm.dataset, func.count())
    sql = sql.group_by(EntityOrm.dataset)
    if datasets is not None:
        sql = sql.filter(EntityOrm.dataset.in_(datasets))
    result = session.execute(sql)
    return result.fetchall()


@redis_cache("dataset-entity-counts", model_class=None)
def get_dataset_entity_counts(session: DbSession) -> dict[str, int]:
    """Share dataset counts across list and detail requests using the default TTL."""
    return dict(get_entity_count(session.session))


def get_entities(session, dataset: str, limit: int) -> List[EntityModel]:
    entities = (
        session.query(EntityOrm).filter(EntityOrm.dataset == dataset).limit(limit).all()
    )
    return [entity_factory(e) for e in entities]


# A search that is too broad is expected, so the router reports it as a metric
# and a warning rather than an error.
@log_slow_execution(threshold_seconds=1, expected_exceptions=(EntitySearchTooBroad,))
def get_entity_search(
    session: Session, parameters: dict, extension: Optional[SuffixEntity] = None
):
    params = normalised_params(parameters)

    # Build filtered query once
    basequery = session.query(EntityOrm)
    basequery = _apply_base_filters(basequery, params)
    basequery = _apply_date_filters(basequery, params)
    # Geometry filters are applied by _geometry_match_branches instead.
    basequery = _apply_location_filters(session, basequery, params)
    basequery = _apply_period_option_filter(basequery, params)

    # If there are location filters, we need to use a different approach to get the count and entities.
    if has_location_filters(params):
        return _search_with_capped_matches(session, basequery, params, extension)
    return _search_with_capped_count(session, basequery, params, extension)


def _search_with_capped_count(session, basequery, params, extension):
    # Without a location filter the page can be read in entity order straight from
    # the primary key, so pagination stays stable. Only the count is costly for a
    # broad search, so stop counting at cap + 1 instead of counting every match.
    capped_ids = (
        basequery.with_entities(EntityOrm.entity)
        .limit(ENTITY_SEARCH_COUNT_CAP + 1)
        .subquery()
    )
    count_query = session.query(func.count()).select_from(capped_ids)
    with sentry_sdk.start_span(op="entity.search", name="count.execute_fetch"):
        matched_count = _fetch_with_search_timeout(session, count_query)[0][0]
    count_is_capped = matched_count > ENTITY_SEARCH_COUNT_CAP

    # Above the cap the last page is unknown, so read one extra row to tell
    # whether there is a next page.
    limit = params.get("limit")
    page_params = params
    if count_is_capped and limit is not None:
        page_params = {**params, "limit": limit + 1}
    query = _apply_limit_and_pagination_filters(basequery, page_params)
    query = _apply_field_filters(query, params, extension)
    with sentry_sdk.start_span(op="entity.search", name="page.execute_fetch"):
        rows = _fetch_with_search_timeout(session, query)
    has_next_page = limit is not None and len(rows) > limit
    rows = rows[:limit] if limit is not None else rows
    with sentry_sdk.start_span(op="entity.search", name="models.convert"):
        entities = [entity_factory(row) for row in rows]
    result = {
        "params": params,
        "count": min(matched_count, ENTITY_SEARCH_COUNT_CAP),
        "count_is_capped": count_is_capped,
        "entities": entities,
    }
    if count_is_capped:
        result["has_next_page"] = has_next_page
    return result


def _search_with_capped_matches(session, basequery, params, extension):
    # Stop at cap + 1 matches in whatever order the database finds them, then sort
    # only those. At or below the cap the set is complete, so pagination is stable.
    # Above it the set is arbitrary, so only the first page is returned.
    branches = _location_match_branches(session, basequery, params)
    if len(branches) == 1:
        found = branches[0].subquery()
    else:
        found = union_all(*[branch.statement for branch in branches]).subquery()
    matches = (
        select(list(found.c)[0].label("entity"))
        .limit(ENTITY_SEARCH_COUNT_CAP + 1)
        .cte("search_matches")
        .prefix_with("MATERIALIZED", dialect="postgresql")
    )
    total = select(func.count().label("total")).select_from(matches).subquery()
    page = (
        select(matches.c.entity)
        .order_by(matches.c.entity)
        .limit(params.get("limit"))
        .offset(params.get("offset"))
        .cte("search_page")
    )
    # Keep the total even when the requested page is empty.
    query = (
        session.query(EntityOrm)
        .select_from(total)
        .outerjoin(page, true())
        .outerjoin(EntityOrm, EntityOrm.entity == page.c.entity)
        .order_by(page.c.entity)
    )
    query = _apply_field_filters(query, params, extension)
    orm_result = query.is_single_entity
    query = query.add_columns(
        total.c.total.label("_search_count"),
        page.c.entity.label("_matched_entity"),
    )
    with sentry_sdk.start_span(op="entity.search", name="shared_query.execute_fetch"):
        rows = _fetch_with_search_timeout(session, query)

    matched_count = rows[0]._search_count
    count_is_capped = matched_count > ENTITY_SEARCH_COUNT_CAP
    if count_is_capped and params.get("offset"):
        rows = []
    with sentry_sdk.start_span(op="entity.search", name="models.convert"):
        entities = [
            entity_factory(row[0] if orm_result else row)
            for row in rows
            if row._matched_entity is not None
        ]
    return {
        "params": params,
        "count": min(matched_count, ENTITY_SEARCH_COUNT_CAP),
        "count_is_capped": count_is_capped,
        "pagination_is_capped": count_is_capped,
        "entities": entities,
    }


def _location_match_branches(session, basequery, params):
    """Build the queries whose first column is the ID of each matching entity."""
    if params.get("geometry"):
        return _geometry_match_branches(basequery, params)

    if params.get("geometry_curie") and not has_location_filters(
        params, include_curie=False
    ):
        # Both spatial branches already include base, date and period filters,
        # so read their matches without looking up the entity rows again.
        matches = _curie_matches(session, params)
        query = session.query(matches.c.matched_entity)
        if len(params["geometry_curie"]) > 1:
            query = query.group_by(matches.c.matched_entity)
        return [query]

    return [basequery.with_entities(EntityOrm.entity)]


def _geometry_match_branches(basequery, params):
    # Filter entity directly so the cap can stop the scan early, instead of
    # collecting every match through an IN subquery.
    #
    # With a dataset filter, test geometry OR point in one branch. Postgres can then
    # walk the dataset index and stop at the cap, which was fastest for broad
    # searches on one dataset.
    #
    # Without one, an OR across the two columns makes Postgres build a bitmap of
    # every match in the box before returning any rows, which timed out for broad
    # boxes. Splitting geometry and point into separate branches lets each stream
    # from its own spatial index instead. The point branch skips entities the
    # geometry branch already matched, so no entity is returned twice.
    #
    # Subdivided datasets stay in their own branch, because an OR with their
    # subquery would rule the entity indexes out. A dataset is only ever in one of
    # the entity or subdivided branches.
    subdivided = aliased(EntitySubdividedOrm)
    subdivided_filter, entity_filter = _dataset_filters(params, subdivided)
    spatial_function = get_spatial_function_for_relation(
        params.get("geometry_relation", GeometryRelation.within)
    )
    geometries = [
        func.ST_GeomFromText(geometry, 4326) for geometry in params["geometry"]
    ]

    def column_matches(column):
        return and_(
            column.is_not(None),
            func.ST_IsValid(column),
            or_(*[spatial_function(column, geom) for geom in geometries]),
        )

    branches = []
    if entity_filter is not None:
        geometry_matches = column_matches(EntityOrm.geometry)
        point_matches = column_matches(EntityOrm.point)
        if params.get("dataset"):
            conditions = [or_(geometry_matches, point_matches)]
        else:
            conditions = [geometry_matches, and_(point_matches, not_(geometry_matches))]
        for condition in conditions:
            branches.append(
                basequery.filter(entity_filter, condition).with_entities(
                    EntityOrm.entity
                )
            )
    if subdivided_filter is not None:
        subdivided_ids = select(subdivided.entity).where(
            subdivided_filter,
            subdivided.geometry_subdivided.isnot(None),
            func.ST_IsValid(subdivided.geometry_subdivided),
            or_(
                *[
                    spatial_function(subdivided.geometry_subdivided, geom)
                    for geom in geometries
                ]
            ),
        )
        branches.append(
            basequery.filter(EntityOrm.entity.in_(subdivided_ids)).with_entities(
                EntityOrm.entity
            )
        )
    return branches


def _fetch_with_search_timeout(session, query):
    settings = get_settings()
    _set_local_statement_timeout(session, settings.ENTITY_SEARCH_STATEMENT_TIMEOUT_MS)
    try:
        rows = query.all()
    except OperationalError as error:
        if not _is_statement_timeout(error):
            raise
        # Rolling back clears the aborted transaction and the local timeout, so the
        # rest of the request can still use this session.
        session.rollback()
        raise EntitySearchTooBroad() from error
    # Later queries in this transaction keep the normal timeout.
    _set_local_statement_timeout(session, settings.DB_STATEMENT_TIMEOUT_MS)
    return rows


def _is_statement_timeout(error):
    # 57014 also covers admin cancels and read-replica recovery conflicts, which are
    # real incidents rather than broad searches, so check the message as well.
    return getattr(error.orig, "pgcode", None) == PG_QUERY_CANCELED and (
        "statement timeout" in str(error.orig)
    )


def _set_local_statement_timeout(session, timeout_ms):
    session.execute(select(func.set_config("statement_timeout", str(timeout_ms), True)))


def get_entity_map_lpa(session: Session, parameters: dict):
    """
    Retrieves a local planning authority entity whose name starts with
    the query string passed in the parameters.

    Uses prefix matching (name starts with query) which can efficiently
    use the B-tree index on the name column.
    """

    if parameters is None:
        return None

    name_query = parameters.get("name")
    if not name_query or not isinstance(name_query, str):
        return None

    # Prefix match - can use btree index efficiently
    query = (
        session.query(EntityOrm)
        .filter(EntityOrm.dataset == "local-planning-authority")
        .filter(EntityOrm.name.ilike(f"{name_query}%"))
        .order_by(func.lower(EntityOrm.name))
    )

    entity = query.first()
    return entity_factory(entity) if entity else None


def _apply_field_filters(query, params, extension: Optional[SuffixEntity] = None):
    include_fields = params.get("field", [])
    exclude_fields = params.get("exclude_field", [])
    # disable field filters if geojson as we already need to get them all
    if extension and extension == SuffixEntity.geojson:
        return query

    if not include_fields and not exclude_fields:
        if extension and extension == SuffixEntity.json:
            # json response always drops geojson, so select the table columns only.
            return query.with_entities(*EntityOrm.__table__.columns)
        # HTML responses render the geojson, so leave the query alone.
        return query

    # if requested specific fields only request those from db:
    if include_fields:
        fields = set([s.strip() for sub in include_fields for s in sub.split(",") if s])
        if extension:
            fields.add(extension.value)
        columns = [
            column
            for column in EntityOrm.__table__.columns
            if column.name in fields
            or (column.name == "entity")  # return at least entity column
        ]
    else:
        # if no fields specified then use all columns
        # need to make copy of columns for editing later otherwise they are immutable
        columns = [column for column in EntityOrm.__table__.columns]

    # now remove the exclude fields from included fields
    if exclude_fields:
        # Split the comma-separated string into a list of individual fields
        split_strings = [
            s.strip() for sub in exclude_fields for s in sub.split(",") if s
        ]
        exclude_fields = set(split_strings)

        # Dynamically construct the selected columns by excluding the specified fields
        selected_columns = [
            column for column in columns if column.name not in exclude_fields
        ]
        if not selected_columns:
            raise ValueError(
                "No columns left to select after exclusions. Please check the field names."
            )
    else:
        selected_columns = columns

    # Modify the query to select only the desired columns
    query = query.with_entities(*selected_columns)

    return query


def lookup_entity_link(
    session: Session, reference: str, dataset: str, organisation_entity: int = None
):
    """
    This function takes an entity and a list of fields that are entity links.
    any entity link fields are then replaced with the entity object.
    """
    search_params = {"reference": [reference], "dataset": [dataset]}

    # Normally we filter by dataset, reference, and organisation.
    # For 'listed-building', we exclude organisation to match Historic England data.
    if dataset != "listed-building" and organisation_entity is not None:
        search_params["organisation_entity"] = [organisation_entity]

    try:
        found_entities = get_entity_search(session, search_params)
    except EntitySearchTooBroad:
        # A linked entity is optional on the entity page, so show the page without it.
        record_search_too_broad("entity_link", [dataset])
        return None
    if found_entities["count"] == 1:
        found_entity = found_entities["entities"][0]
        return found_entity.model_dump(by_alias=True, exclude={"geojson"})
    # elif found_entities["count"] > 1:
    # Log that multiple entities were found
    # set the entity to -1 so the page not found page is shown
    # elif found_entities["count"] == 0:
    # Log that no entity was found
    # set the entity to -1 so the page not found page is shown


def _apply_base_filters(query, params):
    # exclude any params that match an entity field name but need special handling
    excluded = set(["geometry"])

    for key, val in params.items():
        if key not in excluded and hasattr(EntityOrm, key):
            field = getattr(EntityOrm, key)
            if isinstance(val, list):
                query = query.filter(field.in_(val))
            else:
                query = query.filter(field == val)

    if params.get("curie") is not None:
        curies = params.get("curie")
        for curie in curies:
            query = _apply_curie_filter(curie, query)

    if params.get("organisation") is not None:
        organisation_curies = params.get("organisation")
        for curie in organisation_curies:
            query = _apply_curie_filter(curie, query)

    return query


def _apply_curie_filter(curie, query):
    parts = curie.split(":")
    if len(parts) == 2:
        prefix, reference = parts
        query = query.filter(
            EntityOrm.prefix == prefix, EntityOrm.reference == reference
        )
    return query


def _apply_date_filters(query, params):
    for date_field in ["start_date", "end_date", "entry_date"]:
        field = get_date_field_to_filter(date_field)
        date = get_date_to_filter(date_field, params)
        op = get_operator(params)
        if field is not None and date is not None and op is not None:
            query = query.filter(op(field, date))
    return query


def _dataset_filters(params, subdivided_alias):
    """
    Build the dataset restriction for each branch of the spatial subqueries.

    Returns (subdivided_filter, entity_filter). Either may be None, meaning that
    branch cannot contribute any rows and should be skipped entirely.
    """
    requested = params.get("dataset") or []
    if not requested:
        # No dataset filter, so both branches keep their original scope.
        return (
            subdivided_alias.dataset.in_(complex_datasets),
            EntityOrm.dataset.notin_(complex_datasets),
        )

    complex_requested = [d for d in requested if d in complex_datasets]
    simple_requested = [d for d in requested if d not in complex_datasets]
    return (
        subdivided_alias.dataset.in_(complex_requested) if complex_requested else None,
        EntityOrm.dataset.in_(simple_requested) if simple_requested else None,
    )


def _union_of(branches):
    if len(branches) == 1:
        return branches[0]
    return union_all(*branches)


def _curie_matches(session, params):
    split_curies = [tuple(curie.split(":")) for curie in params["geometry_curie"]]
    return _boundary_matches(
        session,
        params,
        tuple_(EntityOrm.prefix, EntityOrm.reference).in_(split_curies),
        "curie_boundaries",
    )


def _boundary_matches(session, params, boundary_filter, boundary_name):
    """Match polygons and points separately, keeping each entity-boundary pair."""
    spatial_function = get_spatial_function_for_relation(
        params.get("geometry_relation", GeometryRelation.within)
    )
    boundaries = (
        select(EntityOrm.entity.label("boundary_entity"), EntityOrm.geometry)
        .where(
            boundary_filter,
            EntityOrm.geometry.is_not(None),
            func.ST_IsValid(EntityOrm.geometry),
        )
        .cte(boundary_name)
        .prefix_with("MATERIALIZED", dialect="postgresql")
    )
    branches = []
    for column in (EntityOrm.geometry, EntityOrm.point):
        conditions = [
            column.is_not(None),
            spatial_function(column, boundaries.c.geometry),
        ]
        if column is EntityOrm.geometry:
            conditions.append(func.ST_IsValid(column))
        branch = session.query(
            EntityOrm.entity.label("matched_entity"), boundaries.c.boundary_entity
        ).join(boundaries, and_(*conditions))
        # Push cheap filters into both spatial scans, not just the outer query.
        branch = _apply_base_filters(branch, params)
        branch = _apply_date_filters(branch, params)
        branch = _apply_period_option_filter(branch, params)
        branches.append(branch)

    # Deduplicate geometry/point matches for each entity-boundary pair.
    # Keeping boundary identity preserves multiplicity until the outer query
    # applies the existing grouping rules for each location filter.
    return branches[0].union(branches[1]).subquery()


def _apply_location_filters(session, query, params):
    point = get_point(params)
    entity_subdivided_alias = aliased(EntitySubdividedOrm)
    subdivided_filter, entity_filter = _dataset_filters(params, entity_subdivided_alias)

    if point is not None:
        branches = []

        # Pre-filter EntitySubdividedOrm table
        if subdivided_filter is not None:
            branches.append(
                select(entity_subdivided_alias.entity).where(
                    subdivided_filter,
                    entity_subdivided_alias.geometry_subdivided.isnot(None),
                    func.ST_IsValid(entity_subdivided_alias.geometry_subdivided),
                    func.ST_Contains(
                        entity_subdivided_alias.geometry_subdivided,
                        func.ST_GeomFromText(point, 4326),
                    ),
                )
            )

        #  Pre-filter EntityOrm table
        if entity_filter is not None:
            branches.append(
                select(EntityOrm.entity).where(
                    entity_filter,
                    EntityOrm.geometry.isnot(None),
                    func.ST_IsValid(EntityOrm.geometry),
                    func.ST_Contains(
                        EntityOrm.geometry, func.ST_GeomFromText(point, 4326)
                    ),
                )
            )

        # Combine using union_all
        union_ids = _union_of(branches).subquery()

        # Step 2: Get full EntityOrm rows matching those IDs
        query = query.filter(EntityOrm.entity.in_(select(union_ids.c.entity)))

    intersecting_entities = params.get("geometry_entity", [])
    if intersecting_entities:
        matches = _boundary_matches(
            session,
            params,
            EntityOrm.entity.in_(intersecting_entities),
            "entity_boundaries",
        )
        query = query.join(matches, EntityOrm.entity == matches.c.matched_entity)

    references = params.get("geometry_reference", [])
    if references:
        matches = _boundary_matches(
            session,
            params,
            EntityOrm.reference.in_(references),
            "reference_boundaries",
        )
        query = query.join(matches, EntityOrm.entity == matches.c.matched_entity)

    curies = params.get("geometry_curie", [])
    if curies:
        matches = _curie_matches(session, params)
        query = query.join(matches, EntityOrm.entity == matches.c.matched_entity)

    # final step to add a group by if more than one condition is being met.
    if len(intersecting_entities) > 1 or len(references) > 0 or len(curies) > 1:
        # if len(intersecting_entities) > 1 or len(curies) > 1:
        query = query.group_by(EntityOrm.entity)
    elif len(intersecting_entities) + len(curies) > 1:
        query = query.group_by(EntityOrm)

    return query


def _apply_period_option_filter(query, params):
    options = params.get("period", PeriodOption.all)
    if options == PeriodOption.all or PeriodOption.all in options:
        return query
    elif PeriodOption.current in options and PeriodOption.historical in options:
        return query
    elif PeriodOption.current in options:
        return query.filter(
            or_(EntityOrm.end_date.is_(None), EntityOrm.end_date > func.now())
        )
    elif PeriodOption.historical in options:
        return query.filter(
            and_(EntityOrm.end_date.is_not(None), EntityOrm.end_date < func.now())
        )


def _apply_limit_and_pagination_filters(query, params):
    query = query.order_by(EntityOrm.entity)
    if params.get("limit") is not None:
        query = query.limit(params["limit"])
    if params.get("offset") is not None:
        query = query.offset(params["offset"])
    return query


def get_linked_entities(
    session: Session, dataset: str, reference: str, linked_dataset: str = None
) -> List[EntityModel]:
    query = (
        session.query(EntityOrm)
        .filter(EntityOrm.dataset == dataset)
        .filter(EntityOrm.json.contains({linked_dataset: reference}))
    )

    if dataset in ["local-plan-timetable"]:
        query = query.order_by(cast(EntityOrm.json["event-date"].astext, Date).desc())

    entities = query.all()
    return [entity_factory(e) for e in entities]


def fetchEntityFromReference(
    session: Session, dataset: str, reference: str
) -> EntityModel:
    entity = (
        session.query(EntityOrm)
        .filter(EntityOrm.dataset == dataset)
        .filter(EntityOrm.reference == reference)
    ).one_or_none()

    if entity:
        return entity_factory(entity)
    return None


@redis_cache("organisations", model_class=EntityModel)
def get_organisations(session: DbSession) -> List[EntityModel]:
    organisations = (
        session.session.query(EntityOrm)
        .filter(EntityOrm.typology == "organisation")
        .filter(EntityOrm.organisation_entity.isnot(None))
        .filter(EntityOrm.name.isnot(None))
        .distinct()
        .all()
    )
    if organisations:
        return [entity_factory(e) for e in organisations]
    else:
        return []
