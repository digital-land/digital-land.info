from unittest.mock import patch
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool

from application.db.pool_metrics import _checkout_caller, instrument_pool
from application.db.session import _create_engine


def test_engine_is_always_instrumented():
    with (
        patch("application.db.session.get_settings"),
        patch("application.db.session.create_engine") as create,
        patch("application.db.session.instrument_pool") as instrument,
    ):
        assert _create_engine() is create.return_value
        instrument.assert_called_once_with(create.return_value)


@pytest.fixture
def measured_pool():
    engine = create_engine("sqlite://", poolclass=QueuePool)
    instrument_pool(engine)
    with patch("application.db.pool_metrics.sentry_sdk.metrics") as metrics:
        yield engine, metrics
    engine.dispose()


@pytest.mark.parametrize("invalidate", [False, True])
def test_connection_hold_duration(measured_pool, invalidate):
    engine, metrics = measured_pool
    with patch("application.db.pool_metrics.perf_counter", side_effect=[10, 12.5]):
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            metrics.distribution.assert_not_called()
            if invalidate:
                connection.invalidate()

    call = metrics.distribution.call_args
    assert call.args == ("db.pool.connection_hold_duration", 2.5)
    assert call.kwargs["unit"] == "second"
    assert [call.args[1] for call in metrics.gauge.call_args_list] == [1, 0]
    assert engine.pool.checkedout() == 0


def test_concurrent_checkouts(measured_pool):
    engine, metrics = measured_pool
    with engine.connect():
        with engine.connect():
            pass
    assert [call.args[1] for call in metrics.gauge.call_args_list] == [1, 2, 1, 0]
    assert metrics.distribution.call_count == 2


def test_telemetry_failure_does_not_break_queries_or_cleanup(measured_pool):
    engine, metrics = measured_pool
    metrics.gauge.side_effect = RuntimeError("Telemetry unavailable")
    metrics.distribution.side_effect = RuntimeError("Telemetry unavailable")
    with pytest.raises(ValueError):
        with engine.connect() as connection:
            assert connection.execute(text("SELECT 1")).scalar() == 1
            raise ValueError("Application error")
    assert engine.pool.checkedout() == 0


def test_caller_detection():
    frame = None
    for module, function in [
        ("application.routers.entity", "search_entities"),
        ("application.data_access.entity_queries", "get_entity_search"),
        ("sqlalchemy.pool.base", "checkout"),
        ("application.db.pool_metrics", "checkout"),
    ]:
        frame = SimpleNamespace(
            f_globals={"__name__": module},
            f_code=SimpleNamespace(co_name=function),
            f_back=frame,
        )
    with patch("application.db.pool_metrics.sys._getframe", return_value=frame):
        assert _checkout_caller() == {
            "operation": "application.routers.entity.search_entities",
            "checkout_function": (
                "application.data_access.entity_queries.get_entity_search"
            ),
        }


def test_caller_detection_unavailable():
    with patch("application.db.pool_metrics.sys._getframe", side_effect=ValueError):
        assert _checkout_caller() == {
            "operation": "unknown",
            "checkout_function": "unknown",
        }


@pytest.mark.parametrize("invalidate", [False, True])
def test_checkout_caller_survives_until_return_and_is_refreshed(
    measured_pool, invalidate
):
    engine, metrics = measured_pool
    callers = [{"operation": "first"}, {"operation": "second"}]
    with (
        patch("application.db.pool_metrics._checkout_caller", side_effect=callers),
        patch("application.db.pool_metrics.logger.info") as log,
    ):
        for expected in callers:
            with engine.connect() as connection:
                if invalidate:
                    connection.invalidate()
            assert (
                metrics.distribution.call_args.kwargs["attributes"]["operation"]
                == expected["operation"]
            )
            assert log.call_args.kwargs["extra"]["operation"] == expected["operation"]
    assert "operation" not in metrics.gauge.call_args.kwargs["attributes"]
