"""Connection occupancy measurements for before/after load tests."""

import logging
import os
import sys
from threading import Lock
from time import perf_counter

import sentry_sdk
from sentry_sdk.integrations.logging import SentryLogsHandler
from sqlalchemy import event

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# Send these INFO records to Sentry without lowering the application's log level.
logger.addHandler(SentryLogsHandler(level=logging.INFO))


def _checkout_caller():
    """Capture code names only; never retain frames, arguments or local values."""
    caller = {"operation": "unknown", "checkout_function": "unknown"}
    frame = None
    try:
        frame = sys._getframe(1)
        while frame is not None:
            module = frame.f_globals.get("__name__", "")
            if module.startswith("application.") and module != __name__:
                name = f"{module}.{frame.f_code.co_name}"
                if caller["checkout_function"] == "unknown":
                    caller["checkout_function"] = name
                if module.startswith("application.routers."):
                    caller["operation"] = name
                    break
            frame = frame.f_back
    except Exception:
        # Missing stack information must not affect database access.
        pass
    finally:
        del frame
    return caller


def instrument_pool(engine):
    """Measure successful checkouts until check-in, not time waiting for a slot."""
    lock = Lock()
    active = 0
    attributes = {"pool": "read", "worker_pid": os.getpid()}
    timer_key = "pool_metrics_checkout_started"
    caller_key = "pool_metrics_checkout_caller"

    @event.listens_for(engine, "checkout")
    def checkout(connection, record, proxy):
        nonlocal active
        started = perf_counter()
        caller = _checkout_caller()
        # record_info survives connection invalidation, unlike info.
        with lock:
            record.record_info[timer_key] = started
            record.record_info[caller_key] = caller
            active += 1
            emit_usage(active)

    @event.listens_for(engine, "checkin")
    def checkin(connection, record):
        nonlocal active
        with lock:
            started = record.record_info.pop(timer_key, None)
            if started is None:
                return
            caller = record.record_info.pop(caller_key, {})
            duration = perf_counter() - started
            active -= 1
            emit_usage(active)
        try:
            sentry_sdk.metrics.distribution(
                "db.pool.connection_hold_duration",
                duration,
                unit="second",
                attributes={**attributes, **caller},
            )
            logger.info(
                "Database connection returned to pool",
                extra={
                    **attributes,
                    **caller,
                    "connection_hold_seconds": duration,
                },
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
