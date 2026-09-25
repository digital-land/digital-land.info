from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from application.core import search_trace
from application.routers import entity


@pytest.fixture
def comparison_client(mocker):
    session = MagicMock()
    app = FastAPI()
    app.include_router(entity.router, prefix="/entity")
    app.include_router(entity.comparison_router, prefix="/entity2")
    app.dependency_overrides[entity.get_session] = lambda: session
    app.dependency_overrides[entity.get_redis] = lambda: None
    mocker.patch.object(entity, "get_dataset_names", return_value=["listed-building"])
    mocker.patch.object(entity, "get_typology_names", return_value=[])
    mocker.patch.object(entity, "make_links", return_value={})
    result = {"params": {"limit": 10}, "count": 0, "entities": []}
    optimized = mocker.patch.object(entity, "get_entity_search", return_value=result)
    baseline = mocker.patch.object(
        entity, "get_entity_search_baseline", return_value=result
    )
    return TestClient(app), session, optimized, baseline


def test_comparison_routes_select_independent_searches(comparison_client, caplog):
    client, session, optimized, baseline = comparison_client
    params = [
        ("geometry_curie", "statistical-geography:E12000007"),
        ("geometry_curie", "statistical-geography:E09000007"),
        ("dataset", "listed-building"),
        ("period", "current"),
        ("limit", "10"),
    ]
    for path in ("/entity.json", "/entity2.json"):
        response = client.get(path, params=params)
        assert response.status_code == 200
        assert response.json() == {"entities": [], "links": {}, "count": 0}
    optimized.assert_called_once()
    baseline.assert_called_once()
    assert optimized.call_args.args[1:] == baseline.call_args.args[1:]
    assert session.connection.call_count == 2
    ends = [r for r in caplog.records if r.message == "entity.search.stage.end"]
    totals = [r for r in ends if r.stage == "request.total"]
    assert {r.search_variant for r in totals} == {"optimized", "main"}
    assert len({r.search_parameters_hash for r in totals}) == 1
    assert len({r.search_request_id for r in totals}) == 2
    assert {r.stage for r in ends} >= {
        "db.acquire_connection",
        "metadata.datasets",
        "metadata.typologies",
        "area.lookup",
        "filters.validate",
        "response.format",
        "request.total",
    }
    assert all(r.duration_ms >= 0 and r.outcome == "success" for r in ends)


def test_connection_failure_records_stage_and_preserves_error(
    comparison_client, caplog
):
    client, session, optimized, baseline = comparison_client
    session.connection.side_effect = RuntimeError("pool unavailable")
    with pytest.raises(RuntimeError, match="pool unavailable"):
        client.get("/entity2.json")
    ends = [r for r in caplog.records if r.message == "entity.search.stage.end"]
    assert [(r.stage, r.outcome) for r in ends] == [
        ("db.acquire_connection", "error"),
        ("request.total", "error"),
    ]
    assert search_trace._context.get() is None


def test_response_sizes_and_hash_ignore_links_but_detect_record_changes(
    comparison_client, mocker, caplog
):
    from application.core.models import EntityModel

    client, session, optimized, baseline = comparison_client
    original = EntityModel(entity=1, name="Café")
    for search in (optimized, baseline):
        search.return_value = {
            "params": {"limit": 10},
            "count": 25,
            "entities": [original],
        }
    mocker.patch.object(
        entity,
        "make_links",
        side_effect=lambda scheme, netloc, path, query, data: {"self": path},
    )
    responses = [client.get(path) for path in ("/entity.json", "/entity2.json")]
    totals = [
        r
        for r in caplog.records
        if r.message == "entity.search.stage.end" and r.stage == "request.total"
    ]
    assert all(r.total_matches == 25 and r.returned_rows == 1 for r in totals)
    assert [r.response_body_bytes for r in totals] == [
        len(r.content) for r in responses
    ]
    assert totals[0].results_bytes == totals[1].results_bytes
    assert totals[0].results_sha256 == totals[1].results_sha256
    assert responses[0].json()["links"] != responses[1].json()["links"]
    baseline.return_value = {
        "params": {"limit": 10},
        "count": 25,
        "entities": [EntityModel(entity=2, name="Café")],
    }
    client.get("/entity2.json")
    latest = [
        r
        for r in caplog.records
        if r.message == "entity.search.stage.end" and r.stage == "request.total"
    ][-1]
    assert latest.returned_rows == totals[0].returned_rows
    assert latest.results_bytes == totals[0].results_bytes
    assert latest.results_sha256 != totals[0].results_sha256


def test_measurement_failure_preserves_response(comparison_client, mocker):
    client, session, optimized, baseline = comparison_client
    mocker.patch.object(
        search_trace, "_record_response", side_effect=RuntimeError("measurement failed")
    )
    response = client.get("/entity2.json")
    assert response.status_code == 200
    assert response.json()["count"] == 0
