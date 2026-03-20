from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Query
from application.data_access.entity_queries import (
    _apply_limit_and_pagination_filters,
    _apply_location_filters,
    get_entity_query,
)
from application.db.models import EntityOrm
from application.db.session import get_context_session


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


def test_get_entity_query_closes_session():
    """
    Test that `get_entity_query()` properly closes its session after use.

    This is to prevent:
    'QueuePool limit of size 10 overflow 20 reached, connection timed out'
    """
    mock_session = MagicMock()
    mock_session.query.return_value.filter.return_value.one_or_none.return_value = None
    mock_session.query.return_value.get.return_value = None

    with patch(
        "application.data_access.entity_queries.get_context_session"
    ) as mock_context:
        mock_context.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_context.return_value.__exit__ = MagicMock(return_value=False)

        get_entity_query(12345)

        # Verify context manager was used and closed at the
        # end of the session
        mock_context.return_value.__enter__.assert_called_once()
        mock_context.return_value.__exit__.assert_called_once()


def test_get_entity_query_no_pool_exhaustion():
    """
    Test that calling `get_entity_query()` many times
    (more than pool size + overflow) does not exhaust connections,
    ensuring sessions are closed automatically.
    """
    mock_session = MagicMock()
    mock_session.query.return_value.filter.return_value.one_or_none.return_value = None
    mock_session.query.return_value.get.return_value = None

    sessions_created = []
    sessions_closed = []

    def mock_session_factory():
        session = MagicMock()
        session.query.return_value.filter.return_value.one_or_none.return_value = None
        session.query.return_value.get.return_value = None
        sessions_created.append(session)

        def track_close():
            sessions_closed.append(session)

        session.close = track_close
        return session

    with patch("application.db.session.SessionLocal", side_effect=mock_session_factory):

        with patch(
            "application.data_access.entity_queries.get_context_session",
            get_context_session,
        ):
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
