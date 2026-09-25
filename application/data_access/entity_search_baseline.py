"""Temporary comparison baseline from main at 3bf1be43; preserve query semantics."""

from typing import Optional
from sqlalchemy import select, func, or_, and_, tuple_
from sqlalchemy.orm import Session, aliased
from application.core.models import entity_factory
from application.core.search_metrics import measure_entity_search
from application.core.search_trace import search_stage
from application.db.models import EntityOrm, EntitySubdividedOrm
from application.search.enum import GeometryRelation, SuffixEntity
from application.data_access.entity_query_helpers import (
    normalised_params,
    get_point,
    get_spatial_function_for_relation,
)
from application.data_access.entity_queries import (
    _apply_base_filters,
    _apply_date_filters,
    _apply_period_option_filter,
    _apply_limit_and_pagination_filters,
    _apply_field_filters,
    _dataset_filters,
    _union_of,
)


@measure_entity_search
def get_entity_search(
    session: Session, parameters: dict, extension: Optional[SuffixEntity] = None
):
    with search_stage("query.build"):
        params = normalised_params(parameters)

        # Build filtered query once
        basequery = session.query(EntityOrm)
        basequery = _apply_base_filters(basequery, params)
        basequery = _apply_date_filters(basequery, params)
        basequery = _apply_location_filters(session, basequery, params)
        basequery = _apply_period_option_filter(basequery, params)

    with search_stage("count_query.build"):
        count_subquery = basequery.with_entities(EntityOrm.entity).subquery()

    # Database 1st call
    with search_stage("count.execute_fetch"):
        count = session.query(func.count()).select_from(count_subquery).scalar()

    with search_stage("page_query.build"):
        query = _apply_limit_and_pagination_filters(basequery, params)
        query = _apply_field_filters(query, params, extension)

    # Database 2nd call
    with search_stage("page.execute_fetch"):
        rows = query.all()
    with search_stage("models.convert"):
        entities = [entity_factory(entity_orm) for entity_orm in rows]
    return {"params": params, "count": count, "entities": entities}


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
            branches.append(
                select(EntityOrm.entity).where(
                    entity_filter,
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
            )

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
