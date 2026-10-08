import logging
import sentry_sdk

from typing import Optional, List, Tuple
from sqlalchemy import select, func, or_, and_, tuple_, union_all, true
from sqlalchemy.orm import Session

from application.core.models import EntityModel, entity_factory
from application.core.search_metrics import measure_entity_search
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
from sqlalchemy.types import Date
from sqlalchemy.sql.expression import cast
from sqlalchemy.orm import aliased

logger = logging.getLogger(__name__)
complex_datasets = ["flood-risk-zone"]


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


def get_entities(session, dataset: str, limit: int) -> List[EntityModel]:
    entities = (
        session.query(EntityOrm).filter(EntityOrm.dataset == dataset).limit(limit).all()
    )
    return [entity_factory(e) for e in entities]


# TODO: this function will be moved in the next PR into a performance
# test folder and use it as a comparison helper/benchmark
def get_entity_search_OLD_VERSION(
    session: Session, parameters: dict, extension: Optional[SuffixEntity] = None
):
    params = normalised_params(parameters)
    count: int
    entities: list[EntityModel]
    subquery = session.query(EntityOrm.entity)
    subquery = _apply_base_filters(subquery, params)
    subquery = _apply_date_filters(subquery, params)
    subquery = _apply_location_filters(session, subquery, params)
    subquery = _apply_period_option_filter(subquery, params).subquery()
    count_query = session.query(func.count()).select_from(subquery)

    count = count_query.scalar()

    query_args = [EntityOrm]
    query = session.query(*query_args)
    query = _apply_base_filters(query, params)
    query = _apply_date_filters(query, params)
    query = _apply_location_filters(session, query, params)
    query = _apply_period_option_filter(query, params)
    query = _apply_limit_and_pagination_filters(query, params)
    query = _apply_field_filters(
        query, params, extension
    )  # Build the query without excluded params

    entities = query.all()
    entities = [entity_factory(entity_orm) for entity_orm in entities]
    return {"params": params, "count": count, "entities": entities}


@log_slow_execution(threshold_seconds=1)
@measure_entity_search
def get_entity_search(
    session: Session, parameters: dict, extension: Optional[SuffixEntity] = None
):
    params = normalised_params(parameters)

    # Build filtered query once
    basequery = session.query(EntityOrm)
    basequery = _apply_base_filters(basequery, params)
    basequery = _apply_date_filters(basequery, params)
    # Diagnostic branch: ignore location filters to isolate their effect on dev.
    basequery = _apply_period_option_filter(basequery, params)

    # Bypass CURIE matching and shared spatial matches as well as the page filter.
    count_subquery = basequery.with_entities(EntityOrm.entity).subquery()

    with sentry_sdk.start_span(op="entity.search", name="count.execute_fetch"):
        count = session.query(func.count()).select_from(count_subquery).scalar()

    query = _apply_limit_and_pagination_filters(basequery, params)
    query = _apply_field_filters(query, params, extension)

    with sentry_sdk.start_span(op="entity.search", name="page.execute_fetch"):
        rows = query.all()
    with sentry_sdk.start_span(op="entity.search", name="models.convert"):
        entities = [entity_factory(entity_orm) for entity_orm in rows]
    return {"params": params, "count": count, "entities": entities}


def _search_with_shared_matches(session, count_subquery, params, extension):
    # Materialise IDs once for both the total and page, not full geometry rows.
    matches = (
        select(list(count_subquery.c)[0].label("entity"))
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

    # Start from the total so an empty page still returns its count.
    query = (
        session.query(EntityOrm)
        .select_from(total)
        .outerjoin(page, true())
        .outerjoin(EntityOrm, EntityOrm.entity == page.c.entity)
        .order_by(page.c.entity)
    )
    query = _apply_field_filters(query, params, extension)
    orm_result = query.is_single_entity

    with sentry_sdk.start_span(op="entity.search", name="shared_query.execute_fetch"):
        rows = query.add_columns(
            total.c.total.label("_search_count"),
            page.c.entity.label("_matched_entity"),
        ).all()
    with sentry_sdk.start_span(op="entity.search", name="models.convert"):
        entities = [
            entity_factory(row[0] if orm_result else row)
            for row in rows
            if row._matched_entity is not None
        ]

    return {"params": params, "count": rows[0]._search_count, "entities": entities}


def _entity_count_subquery(session, basequery, params):
    # Only CURIE-only location searches can use the direct matches shortcut.
    # Otherwise, select IDs from the complete query to preserve all filters
    # and any duplicate matches.
    if not params.get("geometry_curie") or has_location_filters(
        params, include_curie=False
    ):
        return basequery.with_entities(EntityOrm.entity).subquery()

    # Both spatial branches already include base, date and period filters.
    # Count their matches directly without looking up the entity rows again.
    matches = _curie_matches(session, params)
    query = session.query(matches.c.matched_entity)
    if len(params["geometry_curie"]) > 1:
        query = query.group_by(matches.c.matched_entity)
    return query.subquery()


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

    found_entities = get_entity_search(session, search_params)
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

    spatial_function = get_spatial_function_for_relation(
        params.get("geometry_relation", GeometryRelation.within)
    )

    entity_matches = []
    for geometry in params.get("geometry", []):
        geom = func.ST_GeomFromText(geometry, 4326)
        branches = []

        # Entities from entity_subdivided (for complex datasets)
        if subdivided_filter is not None:
            branches.append(
                select(entity_subdivided_alias.entity).where(
                    subdivided_filter,
                    entity_subdivided_alias.geometry_subdivided.isnot(None),
                    func.ST_IsValid(entity_subdivided_alias.geometry_subdivided),
                    spatial_function(entity_subdivided_alias.geometry_subdivided, geom),
                )
            )

        # Entities from EntityOrm (for all other datasets)
        if entity_filter is not None:
            for column in (EntityOrm.geometry, EntityOrm.point):
                branch = select(EntityOrm.entity).where(
                    entity_filter,
                    column.is_not(None),
                    func.ST_IsValid(column),
                    spatial_function(column, geom),
                )
                branch = _apply_base_filters(branch, params)
                branch = _apply_date_filters(branch, params)
                branch = _apply_period_option_filter(branch, params)
                branches.append(branch)

        # Combine results with UNION ALL
        entity_matches.append(_union_of(branches))

    # Combine all geometries' matching entities via UNION ALL
    if entity_matches:
        unioned_entities_subq = _union_of(entity_matches).subquery()
        query = query.filter(
            EntityOrm.entity.in_(select(unioned_entities_subq.c.entity))
        )

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
