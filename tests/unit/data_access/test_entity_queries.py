from sqlalchemy.orm import Query
from application.data_access.entity_queries import (
    _apply_limit_and_pagination_filters,
    _apply_location_filters,
    get_entity_query,
)
from application.db.models import EntityOrm


def test__apply_limit_and_pagination_filters_with_no_filters_applied():
    query = Query(EntityOrm)
    result = _apply_limit_and_pagination_filters(query, params={"dataset": "testing"})
    assert result._limit_clause is None


def test__apply_location_filters_for_frz_dataset(db_session):
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
    assert "flood-risk-zone" in sql_str.split("FROM entity_subdivided")[1]


def test__apply_location_filters_for_simple_dataset(db_session):
    query = Query(EntityOrm)
    result = _apply_location_filters(
        db_session,
        query,
        params={
            "longitude": "-0.3",
            "latitude": "52.35",
            "dataset": ["conservation-area"],
        },
    )
    sql_str = str(result.statement.compile(compile_kwargs={"literal_binds": True}))
    assert "entity_subdivided" in sql_str
    assert "conservation-area" not in sql_str.split("FROM entity_subdivided")[1]


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
    assert "flood-risk-zone" in sql_str.split("FROM entity_subdivided")[1]
    assert "conservation-area" not in sql_str.split("FROM entity_subdivided")[1]


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


def test_get_entity_query_closes_session(mocker):
    """
    Test that `get_entity_query()` properly closes its session after use.

    This prevents QueuePool exhaustion:
    'QueuePool limit of size 10 overflow 20 reached, connection timed out'
    """
    session_closed = []

    def track_session_close():
        session_closed.append(True)

    # Create a mock session that tracks when close() is called
    mock_session = mocker.MagicMock()
    mock_session.query.return_value.filter.return_value.one_or_none.return_value = None
    mock_session.get.return_value = None
    mock_session.close = track_session_close

    # Patch SessionLocal to return our tracked session
    mocker.patch(
        "application.db.session.SessionLocal",
        return_value=mock_session,
    )

    result = get_entity_query(12345)

    # Verify the query returned expected result (no entity found)
    assert result == (None, None, None)
    # Verify session was closed
    assert len(session_closed) == 1, "Session should be closed after get_entity_query"


def test_get_entity_query_no_pool_exhaustion(mocker):
    """
    Test that calling `get_entity_query()` many times
    (more than pool size + overflow) does not exhaust connections,
    ensuring sessions are closed automatically.
    """
    sessions_created = []
    sessions_closed = []

    def mock_session_factory():
        mock_session = mocker.MagicMock()
        mock_session.query.return_value.filter.return_value.one_or_none.return_value = (
            None
        )
        mock_session.get.return_value = None
        sessions_created.append(mock_session)

        def track_close():
            sessions_closed.append(mock_session)

        mock_session.close = track_close
        return mock_session

    mocker.patch(
        "application.db.session.SessionLocal",
        side_effect=mock_session_factory,
    )

    # Call more times than pool_size (10) + overflow (20) = 30
    num_calls = 35
    for i in range(num_calls):
        get_entity_query(i)

    # Check all query sessions are closed
    assert (
        len(sessions_created) == num_calls
    ), f"Expected {num_calls} sessions created, got {len(sessions_created)}"
    assert len(sessions_closed) == num_calls, (
        f"Expected {num_calls} sessions closed, got {len(sessions_closed)}. "
        "Sessions not being closed will cause QueuePool exhaustion."
    )
