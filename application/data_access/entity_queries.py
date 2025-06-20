import logging

from typing import Optional, List, Tuple
from sqlalchemy import select, func, or_, and_, tuple_, union_all
from sqlalchemy.orm import Session

from application.core.models import EntityModel, entity_factory
from application.data_access.entity_query_helpers import (
    get_date_field_to_filter,
    get_date_to_filter,
    get_operator,
    get_point,
    get_spatial_function_for_relation,
    normalised_params,
)
from application.db.models import EntityOrm, OldEntityOrm, EntitySubdividedOrm
from application.search.enum import GeometryRelation, PeriodOption, SuffixEntity
from application.db.session import redis_cache, DbSession
from sqlalchemy.types import Date
from sqlalchemy.sql.expression import cast, true
from sqlalchemy.orm import aliased

logger = logging.getLogger(__name__)


def get_entity_query(
    session: Session,
    id: int,
) -> Tuple[Optional[EntityModel], Optional[int], Optional[int]]:
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
    else:
        entity = session.query(EntityOrm).get(id)
        if not entity:
            return None, None, None
        else:
            return entity_factory(entity), None, None


def get_entity_count(session: Session, dataset: Optional[str] = None):
    sql = select(EntityOrm.dataset, func.count(EntityOrm.entity))
    sql = sql.group_by(EntityOrm.dataset)
    if dataset is not None:
        sql = sql.filter(EntityOrm.dataset == dataset)
    result = session.execute(sql)
    if dataset is not None:
        return result.fetchone()
    else:
        return result.fetchall()


def get_entities(session, dataset: str, limit: int) -> List[EntityModel]:
    entities = (
        session.query(EntityOrm).filter(EntityOrm.dataset == dataset).limit(limit).all()
    )
    return [entity_factory(e) for e in entities]


def get_entity_search(
    session: Session, parameters: dict, extension: Optional[SuffixEntity] = None
):
    params = normalised_params(parameters)
    count: int
    entities: list[EntityModel]
    # get count
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


def _apply_field_filters(query, params, extension: Optional[SuffixEntity] = None):
    include_fields = params.get("field", [])
    exclude_fields = params.get("exclude_field", [])
    # disable field filters if geojson as we already need to get them all
    if (not include_fields and not exclude_fields) or (
        extension and extension == SuffixEntity.geojson
    ):
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

    if organisation_entity is not None:
        search_params["organisation_entity"] = [organisation_entity]

    found_entities = get_entity_search(session, search_params)
    if found_entities["count"] == 1:
        found_entity = found_entities["entities"][0]
        return found_entity.dict(by_alias=True, exclude={"geojson"})
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


def _apply_location_filters(session, query, params):
    point = get_point(params)
    entity_subdivided_alias = aliased(EntitySubdividedOrm)
    requested_datasets = params.get("dataset", [])  # Handle optional dataset filter
    if requested_datasets:
        subdivided_dataset_filter = entity_subdivided_alias.dataset.in_(
            requested_datasets
        )
        entity_dataset_filter = EntityOrm.dataset.in_(requested_datasets)
    else:
        subdivided_dataset_filter = true()  # Accept all datasets
        entity_dataset_filter = true()

    if point is not None:
        # Pre-filter EntitySubdividedOrm table
        subdivided_ids_query = (
            select(entity_subdivided_alias.entity)
            .where(
                subdivided_dataset_filter,
                entity_subdivided_alias.geometry_subdivided.isnot(None),
                func.ST_IsValid(entity_subdivided_alias.geometry_subdivided),
                func.ST_Contains(
                    entity_subdivided_alias.geometry_subdivided,
                    func.ST_GeomFromText(point, 4326),
                ),
            )
            .subquery()
        )

        #  Pre-filter EntityOrm table
        entity_ids_query = select(EntityOrm.entity).where(
            entity_dataset_filter,
            ~EntityOrm.entity.in_(select(subdivided_ids_query)),
            EntityOrm.geometry.isnot(None),
            func.ST_IsValid(EntityOrm.geometry),
            func.ST_Contains(EntityOrm.geometry, func.ST_GeomFromText(point, 4326)),
        )

        # Combine using union_all
        union_ids = union_all(subdivided_ids_query, entity_ids_query).subquery()

        # Step 2: Get full EntityOrm rows matching those IDs
        query = query.filter(EntityOrm.entity.in_(select(union_ids.c.entity)))

    spatial_function = get_spatial_function_for_relation(
        params.get("geometry_relation", GeometryRelation.within)
    )

    entity_matches = []
    for geometry in params.get("geometry", []):
        geom = func.ST_GeomFromText(geometry, 4326)

        # Entities from entity_subdivided (for complex datasets)
        subdivided_query = select(entity_subdivided_alias.entity).where(
            subdivided_dataset_filter,
            entity_subdivided_alias.geometry_subdivided.isnot(None),
            func.ST_IsValid(entity_subdivided_alias.geometry_subdivided),
            spatial_function(entity_subdivided_alias.geometry_subdivided, geom),
        )

        # Entities from EntityOrm (for all other datasets)
        entity_query = select(EntityOrm.entity).where(
            entity_dataset_filter,
            ~EntityOrm.entity.in_(
                select(entity_subdivided_alias.entity).where(subdivided_dataset_filter)
            ),
            or_(
                and_(
                    EntityOrm.geometry.is_not(None),
                    func.ST_IsValid(EntityOrm.geometry),
                    spatial_function(EntityOrm.geometry, geom),
                ),
                and_(
                    EntityOrm.point.is_not(None),
                    func.ST_IsValid(EntityOrm.point),
                    spatial_function(EntityOrm.point, geom),
                ),
            ),
        )

        # Combine results with UNION ALL
        entity_matches.append(subdivided_query.union_all(entity_query))

    # Combine all geometries' matching entities via UNION ALL
    if entity_matches:
        unioned_entities_subq = union_all(*entity_matches).subquery()
        query = query.filter(
            EntityOrm.entity.in_(select(unioned_entities_subq.c.entity))
        )

    intersecting_entities = params.get("geometry_entity", [])
    if intersecting_entities:
        intersecting_entities_query = (
            session.query(EntityOrm.geometry)
            .filter(EntityOrm.entity.in_(intersecting_entities))
            .group_by(EntityOrm.entity)
            .subquery()
        )

        query = query.join(
            intersecting_entities_query,
            or_(
                and_(
                    EntityOrm.geometry.is_not(None),
                    func.ST_IsValid(EntityOrm.geometry),
                    func.ST_IsValid(intersecting_entities_query.c.geometry),
                    spatial_function(
                        EntityOrm.geometry,
                        intersecting_entities_query.c.geometry,
                    ),
                ),
                and_(
                    EntityOrm.point.is_not(None),
                    func.ST_IsValid(intersecting_entities_query.c.geometry),
                    spatial_function(
                        EntityOrm.point, intersecting_entities_query.c.geometry
                    ),
                ),
            ),
        )

    references = params.get("geometry_reference", [])
    if references:
        reference_query = (
            session.query(EntityOrm.geometry)
            .filter(EntityOrm.reference.in_(references))
            .group_by(EntityOrm)
            .subquery()
        )
        query = query.join(
            reference_query,
            or_(
                and_(
                    EntityOrm.geometry.is_not(None),
                    func.ST_IsValid(EntityOrm.geometry),
                    func.ST_IsValid(reference_query.c.geometry),
                    spatial_function(EntityOrm.geometry, reference_query.c.geometry),
                ),
                and_(
                    EntityOrm.point.is_not(None),
                    func.ST_IsValid(reference_query.c.geometry),
                    spatial_function(EntityOrm.point, reference_query.c.geometry),
                ),
            ),
        )

    curies = params.get("geometry_curie", [])
    if curies:
        split_curies = [tuple(curie.split(":")) for curie in curies]
        curie_query = (
            session.query(EntityOrm.geometry)
            .filter(tuple_(EntityOrm.prefix, EntityOrm.reference).in_(split_curies))
            .group_by(EntityOrm)
            .subquery()
        )
        query = query.join(
            curie_query,
            or_(
                and_(
                    EntityOrm.geometry.is_not(None),
                    func.ST_IsValid(EntityOrm.geometry),
                    func.ST_IsValid(curie_query.c.geometry),
                    spatial_function(EntityOrm.geometry, curie_query.c.geometry),
                ),
                and_(
                    EntityOrm.point.is_not(None),
                    func.ST_IsValid(curie_query.c.geometry),
                    spatial_function(EntityOrm.point, curie_query.c.geometry),
                ),
            ),
        )

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
