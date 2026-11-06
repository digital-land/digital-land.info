from sqlalchemy.orm import Query
import pytest

from application.data_access.entity_queries import (
    _apply_limit_and_pagination_filters,
    _apply_location_filters,
    get_entity_query,
    get_entity_count,
)
from application.db.models import EntityOrm


@pytest.mark.parametrize(
    "filters, expected_where",
    [
        ({}, None),
        ({"datasets": ["brownfield-land"]}, "entity.dataset IN ('brownfield-land')"),
        (
            {"datasets": ["brownfield-land", "article-4-direction"]},
            "entity.dataset IN ('brownfield-land', 'article-4-direction')",
        ),
    ],
)
def test_get_entity_count_filters(mocker, filters, expected_where):
    session = mocker.MagicMock()
    result = get_entity_count(session, **filters)
    statement = session.execute.call_args.args[0]
    sql = str(statement.compile(compile_kwargs={"literal_binds": True}))

    if expected_where:
        assert f"WHERE {expected_where}" in sql
    else:
        assert "WHERE" not in sql
    assert "GROUP BY entity.dataset" in sql
    assert result is session.execute.return_value.fetchall.return_value


def test__apply_limit_and_pagination_filters_with_no_filters_applied():
    query = Query(EntityOrm)
    result = _apply_limit_and_pagination_filters(query, params={"dataset": "testing"})
    assert result._limit_clause is None


def test__apply_location_filters_for_frz_dataset(mocker):
    query = Query(EntityOrm)
    result = _apply_location_filters(
        mocker.MagicMock(),
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


def test__apply_location_filters_for_simple_dataset(mocker):
    query = Query(EntityOrm)
    result = _apply_location_filters(
        mocker.MagicMock(),
        query,
        params={
            "longitude": "-0.3",
            "latitude": "52.35",
            "dataset": ["conservation-area"],
        },
    )
    sql_str = str(result.statement.compile(compile_kwargs={"literal_binds": True}))
    # no complex dataset was asked for, so entity_subdivided cannot contribute
    # any rows and should not be scanned at all
    assert "entity_subdivided" not in sql_str


def test__apply_location_filters_for_both(mocker):
    query = Query(EntityOrm)
    result = _apply_location_filters(
        mocker.MagicMock(),
        query,
        params={
            "longitude": "-0.2",
            "latitude": "53.38",
            "dataset": ["conservation-area", "flood-risk-zone"],
        },
    )
    sql_str = str(result.statement.compile(compile_kwargs={"literal_binds": True}))
    subdivided_branch, entity_branch = sql_str.split("UNION ALL")

    # the complex dataset is looked up in entity_subdivided...
    assert "FROM entity_subdivided" in subdivided_branch
    assert "flood-risk-zone" in subdivided_branch
    assert "conservation-area" not in subdivided_branch

    # ...and the simple one in entity, each filtered to only its own datasets
    assert "FROM entity_subdivided" not in entity_branch
    assert "conservation-area" in entity_branch
    assert "flood-risk-zone" not in entity_branch


def test__apply_location_filters_pushes_dataset_into_entity_branch(mocker):
    """
    The requested dataset must be applied inside the spatial subquery, not only
    by the outer query, otherwise every dataset's geometries are searched.
    """
    query = Query(EntityOrm)
    result = _apply_location_filters(
        mocker.MagicMock(),
        query,
        params={
            "geometry": ["MULTIPOLYGON((-0.1 52.5, -0.5 52.3, 0.0 52.1, -0.1 52.5))"],
            "dataset": ["conservation-area"],
        },
    )
    sql_str = str(result.statement.compile(compile_kwargs={"literal_binds": True}))
    spatial_subquery = sql_str.split("WHERE entity.entity IN")[1]
    assert "conservation-area" in spatial_subquery
    assert "NOT IN" not in spatial_subquery


def test__apply_location_filters_without_dataset(mocker):
    query = Query(EntityOrm)
    params = {
        "latitude": "52.35",
        "longitude": "-0.3",
    }

    result = _apply_location_filters(mocker.MagicMock(), query, params)
    sql = str(result.statement.compile(compile_kwargs={"literal_binds": True}))

    assert "ST_Contains" in sql


def test__apply_location_filters_geometry_within(mocker):
    query = Query(EntityOrm)
    params = {"geometry": ["MULTIPOLYGON((-0.1 52.5, -0.5 52.3, 0.0 52.1, -0.1 52.5))"]}

    result = _apply_location_filters(mocker.MagicMock(), query, params)
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

    # Patch _get_session_local so that _get_session_local()() returns our tracked session.
    # get_context_session() calls _get_session_local()() internally and then calls
    # session.close() in its finally block, which is what this test verifies.
    mocker.patch(
        "application.db.session._get_session_local",
        return_value=lambda: mock_session,
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

    # Patch _get_session_local so _get_session_local()() calls mock_session_factory()
    # each time, creating a distinct tracked session per call.
    mocker.patch(
        "application.db.session._get_session_local",
        return_value=mock_session_factory,
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


def _mock_search_settings(mocker):
    mocker.patch("application.data_access.entity_queries.get_settings")


def _compile_postgres(statement):
    from sqlalchemy.dialects import postgresql

    return str(
        statement.compile(
            dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True}
        )
    )


def _capture_capped_search(mocker, parameters, *, matched_count=0, entity=None):
    from sqlalchemy.orm import Session
    from application.data_access.entity_queries import get_entity_search

    _mock_search_settings(mocker)
    session = mocker.Mock(spec=Session)
    session.query.side_effect = lambda *columns: Query(columns)
    captured = {}

    def capture(query):
        captured["sql"] = _compile_postgres(query.statement)
        return [mocker.MagicMock(_search_count=matched_count, _matched_entity=entity)]

    mocker.patch.object(Query, "all", capture)
    mocker.patch(
        "application.data_access.entity_queries.entity_factory",
        side_effect=lambda row: "entity",
    )
    result = get_entity_search(session, parameters)
    return result, captured.get("sql"), session


BOX = "POLYGON((0 0,1 0,1 1,0 1,0 0))"


def test_geometry_search_with_dataset_filters_geometry_or_point_directly(mocker):
    _, sql, _ = _capture_capped_search(
        mocker,
        {
            "dataset": ["title-boundary"],
            "geometry": [BOX],
            "geometry_relation": "intersects",
            "limit": 500,
        },
    )
    matches = sql[: sql.index("search_page AS")]
    assert "AS MATERIALIZED" in matches
    assert "LIMIT 10001" in matches
    assert "ORDER BY" not in matches
    assert "UNION ALL" not in matches
    assert "IN (SELECT" not in matches
    assert "entity_subdivided" not in sql
    assert "ST_Intersects(entity.geometry" in matches
    assert "ST_Intersects(entity.point" in matches
    assert " OR " in matches


def test_geometry_search_without_dataset_splits_geometry_and_point(mocker):
    _, sql, _ = _capture_capped_search(
        mocker,
        {"geometry": [BOX], "geometry_relation": "intersects", "limit": 500},
    )
    matches = sql[: sql.index("search_page AS")]
    geometry_branch, point_branch, subdivided_branch = matches.split("UNION ALL")
    assert "ST_Intersects(entity.geometry" in geometry_branch
    assert "entity.point" not in geometry_branch
    assert "ST_Intersects(entity.point" in point_branch
    # The point branch skips entities the geometry branch already returned.
    assert "NOT (entity.geometry IS NOT NULL" in point_branch
    assert "entity_subdivided" in subdivided_branch


def test_geometry_search_without_dataset_keeps_subdivided_branch_separate(mocker):
    _, sql, _ = _capture_capped_search(
        mocker,
        {"geometry": [BOX], "geometry_relation": "intersects", "limit": 500},
    )
    matches = sql[: sql.index("search_page AS")]
    assert "UNION ALL" in matches
    assert "entity_subdivided" in matches
    assert "flood-risk-zone" in matches


def test_geometry_search_on_complex_dataset_only_uses_subdivided_table(mocker):
    _, sql, _ = _capture_capped_search(
        mocker,
        {
            "dataset": ["flood-risk-zone"],
            "geometry": [BOX],
            "geometry_relation": "intersects",
            "limit": 500,
        },
    )
    matches = sql[: sql.index("search_page AS")]
    assert "UNION ALL" not in matches
    assert "entity_subdivided" in matches


def test_multiple_geometries_are_all_applied(mocker):
    other = "POLYGON((5 5,6 5,6 6,5 6,5 5))"
    _, sql, _ = _capture_capped_search(
        mocker,
        {
            "dataset": ["title-boundary"],
            "geometry": [BOX, other],
            "geometry_relation": "intersects",
            "limit": 500,
        },
    )
    assert BOX in sql and other in sql


@pytest.mark.parametrize(
    "filters",
    [
        {"latitude": 53.0, "longitude": -2.0},
        {"geometry_curie": ["statistical-geography:E1"]},
        {"geometry_entity": [123]},
        {"geometry_reference": ["E1"]},
    ],
)
def test_other_location_filters_are_capped(mocker, filters):
    _, sql, _ = _capture_capped_search(
        mocker, {"dataset": ["title-boundary"], "limit": 500, **filters}
    )
    assert "LIMIT 10001" in sql


@pytest.mark.parametrize(
    "matched_count, offset, expected_count, is_capped, expected_entities",
    [
        (0, 0, 0, False, []),
        (9_999, 500, 9_999, False, ["entity"]),
        (10_000, 500, 10_000, False, ["entity"]),
        (10_001, 0, 10_000, True, ["entity"]),
        (10_001, 500, 10_000, True, []),
    ],
)
def test_capped_search_only_returns_one_page_above_the_cap(
    mocker, matched_count, offset, expected_count, is_capped, expected_entities
):
    result, _, _ = _capture_capped_search(
        mocker,
        {"geometry": [BOX], "limit": 500, "offset": offset},
        matched_count=matched_count,
        entity=1 if matched_count else None,
    )
    assert result["count"] == expected_count
    assert result["count_is_capped"] is is_capped
    assert result["entities"] == expected_entities


def test_search_without_location_filter_keeps_exact_count_and_pagination(mocker):
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import Session
    from application.data_access.entity_queries import get_entity_search

    # Exercise actual SQL counting and pagination without requiring PostGIS.
    engine = create_engine("sqlite://")
    with Session(engine) as session:
        session.execute(
            text("CREATE TABLE entity (entity INTEGER PRIMARY KEY, dataset TEXT)")
        )
        session.execute(
            text("INSERT INTO entity (entity, dataset) VALUES (:entity, :dataset)"),
            [{"entity": i, "dataset": "title-boundary"} for i in range(1, 16)],
        )
        mocker.patch(
            "application.data_access.entity_queries.ENTITY_SEARCH_COUNT_CAP", 5
        )
        mocker.patch(
            "application.data_access.entity_queries.entity_factory",
            side_effect=lambda row: row.entity,
        )
        result = get_entity_search(
            session,
            {
                "dataset": ["title-boundary"],
                "field": ["entity"],
                "limit": 5,
                "offset": 10,
            },
        )
    assert result["count"] == 15
    assert result["entities"] == [11, 12, 13, 14, 15]
    assert "count_is_capped" not in result
    engine.dispose()


def _operational_error(pgcode):
    from sqlalchemy.exc import OperationalError

    orig = Exception("database error")
    orig.pgcode = pgcode
    return OperationalError("SELECT 1", {}, orig)


def test_search_timeout_raises_too_broad_and_rolls_back(mocker):
    from application.data_access.entity_queries import (
        EntitySearchTooBroad,
        _fetch_with_search_timeout,
    )

    _mock_search_settings(mocker)
    session = mocker.MagicMock()
    query = mocker.MagicMock()
    query.all.side_effect = _operational_error("57014")
    with pytest.raises(EntitySearchTooBroad):
        _fetch_with_search_timeout(session, query)
    session.rollback.assert_called_once()


def test_other_database_errors_are_not_reported_as_too_broad(mocker):
    from sqlalchemy.exc import OperationalError
    from application.data_access.entity_queries import _fetch_with_search_timeout

    _mock_search_settings(mocker)
    session = mocker.MagicMock()
    query = mocker.MagicMock()
    query.all.side_effect = _operational_error("08006")
    with pytest.raises(OperationalError):
        _fetch_with_search_timeout(session, query)
    session.rollback.assert_not_called()
