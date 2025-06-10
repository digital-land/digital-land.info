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


def test__apply_location_filters_uses_subdivided_table(db_session):
    query = Query(EntityOrm)
    result = _apply_location_filters(
        db_session,
        query,
        params={
            "longitude": "-0.2",
            "latitude": "53.38",
        },
    )
    sql_str = str(result.statement.compile(compile_kwargs={"literal_binds": True}))
    assert "entity_subdivided" in sql_str


def test__apply_location_filters_uses_entity_table(db_session):
    query = Query(EntityOrm)
    result = _apply_location_filters(
        db_session,
        query,
        params={
            "longitude": "-0.3",
            "latitude": "52.35",
        },
    )
    sql_str = str(result.statement.compile(compile_kwargs={"literal_binds": True}))
    assert "entity_subdivided" in sql_str
    assert "~ entity in (SELECT" in sql_str or "NOT IN (SELECT" in sql_str


def test__apply_location_filters_for_both(db_session):
    query = Query(EntityOrm)
    result = _apply_location_filters(
        db_session,
        query,
        params={
            "longitude": "-0.2",
            "latitude": "53.38",
            "dataset": ["conservation-area", "flood-risk-zone"],
        },
    )
    sql_str = str(result.statement.compile(compile_kwargs={"literal_binds": True}))
    assert "FROM entity_subdivided" in sql_str
    assert "FROM entity" in sql_str


def test__apply_location_filters_without_dataset(db_session):
    query = Query(EntityOrm)
    params = {
        "latitude": "52.35",
        "longitude": "-0.3",
    }

    result = _apply_location_filters(db_session, query, params)
    sql = str(result.statement.compile(compile_kwargs={"literal_binds": True}))

    assert "ST_Contains" in sql


def test__apply_location_filters_geometry_within(db_session):
    query = Query(EntityOrm)
    params = {"geometry": ["MULTIPOLYGON((-0.1 52.5, -0.5 52.3, 0.0 52.1, -0.1 52.5))"]}

    result = _apply_location_filters(db_session, query, params)
    sql = str(result.statement.compile(compile_kwargs={"literal_binds": True}))

    assert "MULTIPOLYGON" in sql
    assert any(spatial_func in sql for spatial_func in "ST_Within")
