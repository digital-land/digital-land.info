from sqlalchemy.orm import Query
from application.data_access.entity_queries import (
    _apply_limit_and_pagination_filters,
    _apply_location_filters,
)
from application.db.models import EntityOrm


def test__apply_limit_and_pagination_filters_with_no_filters_applied():
    query = Query(EntityOrm)
    result = _apply_limit_and_pagination_filters(query, params={"dataset": "testing"})
    assert result._limit_clause is None


def test__apply_location_filters_with_only_frz(db_session):
    query = Query(EntityOrm)
    result = _apply_location_filters(
        db_session,
        query,
        params={
            "longitude": "-0.2",
            "latitude": "53.38",
            "dataset": ["flood-risk-zone"],
        },
    )
    sql_str = str(result.statement.compile(compile_kwargs={"literal_binds": True}))
    assert "entity_subdivided" in sql_str


def test__apply_location_filters_with_frz_and_others(db_session):
    query = Query(EntityOrm)
    result = _apply_location_filters(
        db_session,
        query,
        params={
            "longitude": "-0.2",
            "latitude": "53.38",
            "dataset": ["flood-risk-zone", "conservation-area"],
        },
    )
    sql_str = str(result.statement.compile(compile_kwargs={"literal_binds": True}))
    assert "entity_subdivided" not in sql_str


def test__apply_location_filters_without_frz(db_session):
    query = Query(EntityOrm)
    result = _apply_location_filters(
        db_session,
        query,
        params={
            "longitude": "-0.2",
            "latitude": "53.38",
            "dataset": ["conservation-area"],
        },
    )
    sql_str = str(result.statement.compile(compile_kwargs={"literal_binds": True}))
    assert "entity_subdivided" not in sql_str


def test__apply_location_filters_with_only_frz_geom(db_session):
    query = Query(EntityOrm)
    result = _apply_location_filters(
        db_session,
        query,
        params={"geometry": "MULTIPOLYGON(-2.1 51.3)", "dataset": ["flood-risk-zone"]},
    )
    sql_str = str(result.statement.compile(compile_kwargs={"literal_binds": True}))
    assert "entity_subdivided" in sql_str


def test__apply_location_filters_with_frz_and_others_geom(db_session):
    query = Query(EntityOrm)
    result = _apply_location_filters(
        db_session,
        query,
        params={
            "geometry": "MULTIPOLYGON(-2.1 51.3)",
            "dataset": ["flood-risk-zone", "conservation-area"],
        },
    )
    sql_str = str(result.statement.compile(compile_kwargs={"literal_binds": True}))
    assert "entity_subdivided" not in sql_str


def test__apply_location_filters_without_frz_geom(db_session):
    query = Query(EntityOrm)
    result = _apply_location_filters(
        db_session,
        query,
        params={
            "geometry": "MULTIPOLYGON(-2.1 51.3)",
            "dataset": ["conservation-area"],
        },
    )
    sql_str = str(result.statement.compile(compile_kwargs={"literal_binds": True}))
    assert "entity_subdivided" not in sql_str
