import logging

from typing import Optional, List, Tuple
from sqlalchemy import select, func, or_, and_, tuple_

from application.core.models import EntityModel, entity_factory
from application.data_access.entity_query_helpers import (
    get_date_field_to_filter,
    get_date_to_filter,
    get_operator,
    get_point,
    get_spatial_function_for_relation,
    normalised_params,
)
from application.db.models import EntityOrm, OldEntityOrm
from application.db.session import get_context_session
from application.search.enum import GeometryRelation, EntriesOption

logger = logging.getLogger(__name__)


# TODO - organisation not implemented yet


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
        else:
            entity = session.query(EntityOrm).get(id)
            if not entity:
                return None, None, None
            else:
                return entity_factory(entity), None, None


def get_entity_count(dataset: Optional[str] = None):
    sql = select(EntityOrm.dataset, func.count(func.distinct(EntityOrm.entity)))
    sql = sql.group_by(EntityOrm.dataset)
    if dataset is not None:
        sql = sql.filter(EntityOrm.dataset == dataset)
    with get_context_session() as session:
        result = session.execute(sql)
        if dataset is not None:
            return result.fetchone()
        else:
            return result.fetchall()


def get_entities(dataset: str, limit: int) -> List[EntityModel]:
    with get_context_session() as session:
        entities = (
            session.query(EntityOrm)
            .filter(EntityOrm.dataset == dataset)
            .limit(limit)
            .all()
        )
        return [entity_factory(e) for e in entities]


def get_entity_search(parameters: dict):
    params = normalised_params(parameters)

    with get_context_session() as session:

        query_args = [EntityOrm, func.count(EntityOrm.entity).over().label("count")]
        query = session.query(*query_args)
        query = _apply_base_filters(query, params)
        query = _apply_date_filters(query, params)
        query = _apply_location_filters(session, query, params)
        query = _apply_entries_option_filter(query, params)
        query = _apply_limit_and_pagination_filters(query, params)

        entities = query.all()
        if entities:
            count = entities[0].count
        else:
            count = 0

        entities = [entity_factory(entity.EntityOrm) for entity in entities]
        return {"params": params, "count": count, "entities": entities}


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
            prefix, reference = curie.split(":")
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
    if point is not None:
        query = query.filter(
            and_(
                EntityOrm.geometry.is_not(None),
                func.ST_IsValid(EntityOrm.geometry),
                func.ST_Contains(EntityOrm.geometry, func.ST_GeomFromText(point, 4326)),
            )
        )

    spatial_function = get_spatial_function_for_relation(
        params.get("geometry_relation", GeometryRelation.within)
    )

    clauses = []
    for geometry in params.get("geometry", []):
        clauses.append(
            or_(
                and_(
                    EntityOrm.geometry.is_not(None),
                    func.ST_IsValid(EntityOrm.geometry),
                    spatial_function(
                        EntityOrm.geometry, func.ST_GeomFromText(geometry, 4326)
                    ),
                ),
                and_(
                    EntityOrm.point.is_not(None),
                    func.ST_IsValid(EntityOrm.point),
                    spatial_function(
                        EntityOrm.point, func.ST_GeomFromText(geometry, 4326)
                    ),
                ),
            )
        )
    if clauses:
        query = query.filter(or_(*clauses))

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
                    func.ST_Intersects(
                        EntityOrm.geometry,
                        intersecting_entities_query.c.geometry,
                    ),
                ),
                and_(
                    EntityOrm.point.is_not(None),
                    func.ST_IsValid(intersecting_entities_query.c.geometry),
                    func.ST_Intersects(
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
                    func.ST_Intersects(EntityOrm.geometry, reference_query.c.geometry),
                ),
                and_(
                    EntityOrm.point.is_not(None),
                    func.ST_IsValid(reference_query.c.geometry),
                    func.ST_Intersects(EntityOrm.point, reference_query.c.geometry),
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
                    func.ST_Intersects(EntityOrm.geometry, curie_query.c.geometry),
                ),
                and_(
                    EntityOrm.point.is_not(None),
                    func.ST_IsValid(curie_query.c.geometry),
                    func.ST_Intersects(EntityOrm.point, curie_query.c.geometry),
                ),
            ),
        )

    # final step to add a group by if more than one condition is being met.
    if len(intersecting_entities) > 1 or len(references) > 0 or len(curies) > 1:
        query = query.group_by(EntityOrm)
    elif len(intersecting_entities) + len(curies) > 1:
        query = query.group_by(EntityOrm)

    return query


def _apply_entries_option_filter(query, params):
    option = params.get("entries", EntriesOption.all)
    if option == EntriesOption.all:
        return query
    if option == EntriesOption.current:
        return query.filter(EntityOrm.end_date.is_(None))
    if option == EntriesOption.historical:
        return query.filter(EntityOrm.end_date.is_not(None))


def _apply_limit_and_pagination_filters(query, params):
    query = query.order_by(EntityOrm.entity)
    if params.get("limit") is not None:
        query = query.limit(params["limit"])
    if params.get("offset") is not None:
        query = query.offset(params["offset"])
    return query
