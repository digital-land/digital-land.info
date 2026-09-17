"""Stage timings for diagnosing single-entity connection holds."""

from contextlib import contextmanager
import logging
from time import perf_counter

import sentry_sdk
from sentry_sdk.integrations.logging import SentryLogsHandler

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(SentryLogsHandler(level=logging.INFO))


def _record(stage, started, outcome):
    duration = perf_counter() - started
    attributes = {
        "operation": "application.data_access.entity_queries.get_entity_query",
        "stage": stage,
        "outcome": outcome,
    }
    try:
        sentry_sdk.metrics.distribution(
            "db.entity_lookup.stage_duration",
            duration,
            unit="second",
            attributes=attributes,
        )
        logger.info(
            "Entity lookup stage completed",
            extra={**attributes, "stage_duration_seconds": duration},
        )
    except Exception:
        pass


@contextmanager
def entity_lookup_stage(stage):
    """Record elapsed wall time without changing application exceptions."""
    started = perf_counter()
    outcome = "error"
    try:
        yield
        outcome = "ok"
    finally:
        _record(stage, started, outcome)


@contextmanager
def measured_entity_session(context):
    """Time the original session context's exit, including rollback/check-in."""
    started = None
    outcome = "error"
    try:
        with context as session:
            try:
                yield session
            finally:
                started = perf_counter()
        outcome = "ok"
    finally:
        if started is not None:
            # An error outcome can also mean a body exception propagated
            # through cleanup; it does not prove that close itself failed.
            _record("session_cleanup", started, outcome)
