"""Connection occupancy measurements for before/after load tests."""

import logging
import os
from threading import Lock
from time import perf_counter

import sentry_sdk
from sentry_sdk.integrations.logging import SentryLogsHandler
from sqlalchemy import event

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# Send these INFO records to Sentry without lowering the application's log level.
logger.addHandler(SentryLogsHandler(level=logging.INFO))


def instrument_pool(engine):
    """Measure successful checkouts until check-in, not time waiting for a slot."""
    lock = Lock()
    active = 0
    attributes = {"pool": "read", "worker_pid": os.getpid()}
    timer_key = "pool_metrics_checkout_started"

    @event.listens_for(engine, "checkout")
    def checkout(connection, record, proxy):
        nonlocal active
        # record_info survives connection invalidation, unlike info.
        with lock:
            record.record_info[timer_key] = perf_counter()
            active += 1
            emit_usage(active)

    @event.listens_for(engine, "checkin")
    def checkin(connection, record):
        nonlocal active
        with lock:
            started = record.record_info.pop(timer_key, None)
            if started is None:
                return
            duration = perf_counter() - started
            active -= 1
            emit_usage(active)
        try:
            sentry_sdk.metrics.distribution(
                "db.pool.connection_hold_duration",
                duration,
                unit="second",
                attributes=attributes,
            )
            logger.info(
                "Database connection returned to pool",
                extra={**attributes, "connection_hold_seconds": duration},
            )
        except Exception:
            # Observability must never prevent a connection being returned.
            pass

    def emit_usage(value):
        try:
            sentry_sdk.metrics.gauge(
                "db.pool.checked_out", value, attributes=attributes
            )
        except Exception:
            pass
