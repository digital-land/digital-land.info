import logging

from typing import Optional, List
from sqlalchemy import select, func, or_

from application.core.models import entity_factory
from application.data_access.entity_query_helpers import (
    get_date_field_to_filter,
    get_date_to_filter,
    get_operator,
    get_point,
    get_geometry_params,
    get_spatial_function_for_relation,
    normalised_params,
)
from application.db.models import EntityOrm
from application.db.session import get_context_session

logger = logging.getLogger(__name__)


def get_entity_query(id: int):
    with get_context_session() as session:
        entity = session.query(EntityOrm).get(id)
        if entity is not None:
            return entity_factory(entity)
        else:
            return None


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


def get_entities(dataset: str, limit: int) -> List[EntityOrm]:
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
        query = session.query(
            EntityOrm, func.count(EntityOrm.entity).over().label("count_all")
        )
        query = _apply_base_filters(query, params)
        query = _apply_date_filters(query, params)
        query = _apply_location_filters(query, params)
        query = _apply_limit_and_pagination_filters(query, params)

        entities = query.all()

        if entities:
            count_all = entities[0].count_all
        else:
            count_all = 0

        return {
            "params": params,
            "count_all": count_all,
            "entities": [entity_factory(e.EntityOrm) for e in entities],
        }


def _apply_base_filters(query, params):

    # for params that may also match entity field names but need special handling
    excluded = set(["geometry"])

    for key, val in params.items():
        if key not in excluded and hasattr(EntityOrm, key):
            field = getattr(EntityOrm, key)
            if isinstance(val, list):
                query = query.filter(field.in_(val))
            else:
                query = query.filter(field == val)
    return query


def _apply_date_filters(query, params):
    for date_field in ["start_date", "end_date", "entry_date"]:
        field = get_date_field_to_filter(date_field)
        date = get_date_to_filter(date_field, params)
        op = get_operator(params)
        if field is not None and date is not None and op is not None:
            query = query.filter(op(field, date))
    return query


def _apply_location_filters(query, params):

    point = get_point(params)
    if point is not None:
        query = query.filter(
            func.ST_Contains(EntityOrm.geometry, func.ST_GeomFromText(point, 4326))
        )

    geometry_params = get_geometry_params(params)
    if geometry_params is not None:
        relation = geometry_params["geometry_relation"]
        geometry = geometry_params["geometry"]

        spatial_function = get_spatial_function_for_relation(relation)
        if spatial_function is None:
            return query

        if len(geometry) == 1:
            query = query.filter(
                spatial_function(
                    EntityOrm.geometry, func.ST_GeomFromText(geometry[0], 4326)
                )
            )
        if len(geometry) > 1:
            clauses = []
            for g in geometry:
                clauses.append(
                    spatial_function(EntityOrm.geometry, func.ST_GeomFromText(g, 4326))
                )
            query = query.filter(or_(*clauses))

    # TODO add or to check if point within geometry as well

    return query


def _apply_limit_and_pagination_filters(query, params):
    query = query.order_by(EntityOrm.entity)
    query = query.limit(params["limit"])
    if params.get("offset") is not None:
        query = query.offset(params["offset"])
    return query
