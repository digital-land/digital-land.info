from contextlib import contextmanager
from unittest.mock import patch

import pytest

from application.db.query_metrics import entity_lookup_stage, measured_entity_session


@pytest.mark.parametrize("fails", [False, True])
def test_stage_timing(fails):
    with (
        patch("application.db.query_metrics.perf_counter", side_effect=[10, 12]),
        patch("application.db.query_metrics.sentry_sdk.metrics") as metrics,
    ):
        try:
            with entity_lookup_stage("entity_fetch"):
                if fails:
                    raise ValueError("original")
        except ValueError as error:
            assert str(error) == "original"
        else:
            assert not fails
        call = metrics.distribution.call_args
        assert call.args == ("db.entity_lookup.stage_duration", 2)
        assert call.kwargs["attributes"]["outcome"] == ("error" if fails else "ok")


@pytest.mark.parametrize("failure", [None, "body", "cleanup"])
def test_cleanup_timed_after_body(failure):
    events = []

    @contextmanager
    def session():
        try:
            yield "session"
        finally:
            events.append("cleanup")
            if failure == "cleanup":
                raise ValueError("cleanup")

    def clock():
        events.append("clock")
        return len(events)

    with (
        patch("application.db.query_metrics.perf_counter", side_effect=clock),
        patch("application.db.query_metrics.sentry_sdk.metrics") as metrics,
    ):
        try:
            with measured_entity_session(session()) as value:
                assert value == "session"
                events.append("body")
                if failure == "body":
                    raise ValueError("body")
        except ValueError as error:
            assert str(error) == failure
        else:
            assert failure is None
        assert events == ["body", "clock", "cleanup", "clock"]
        assert metrics.distribution.call_args.kwargs["attributes"]["stage"] == (
            "session_cleanup"
        )


def test_telemetry_failure_is_ignored():
    with patch("application.db.query_metrics.sentry_sdk.metrics") as metrics:
        metrics.distribution.side_effect = RuntimeError("telemetry")
        with entity_lookup_stage("entity_fetch"):
            pass
