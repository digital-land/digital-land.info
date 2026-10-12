import logging
from types import SimpleNamespace
from unittest.mock import patch

import psycopg2
import pytest
import sentry_sdk
from fastapi import FastAPI
from sentry_sdk.transport import Transport
from sqlalchemy.exc import OperationalError, TimeoutError as SqlAlchemyTimeoutError

from application.factory import add_middleware


class RecordingTransport(Transport):
    def __init__(self):
        super().__init__()
        self.envelopes = []

    def capture_envelope(self, envelope):
        self.envelopes.append(envelope)


@pytest.fixture
def sentry_events():
    settings = SimpleNamespace(
        SENTRY_DSN="https://public@example.com/1",
        ENVIRONMENT="test",
        SENTRY_TRACE_SAMPLE_RATE=1.0,
        RELEASE_TAG="test",
    )
    with patch("application.factory.sentry_sdk.init") as initialise:
        add_middleware(FastAPI(), settings)

    transport = RecordingTransport()
    with sentry_sdk.init(
        **initialise.call_args.kwargs,
        transport=transport,
        default_integrations=False,
        auto_enabling_integrations=False,
    ):
        yield transport.envelopes
        sentry_sdk.flush()


@pytest.mark.parametrize(
    "error",
    [
        TimeoutError("request timed out"),
        SqlAlchemyTimeoutError("connection pool timed out"),
        OperationalError("SELECT 1", {}, Exception("statement timeout")),
        psycopg2.OperationalError("connection failed"),
    ],
)
@pytest.mark.parametrize("capture", ["exception", "logging"])
def test_timeout_and_operational_errors_are_not_sent(sentry_events, error, capture):
    if capture == "exception":
        sentry_sdk.capture_exception(error)
    else:
        try:
            raise error
        except Exception:
            logging.getLogger(__name__).exception("Database request failed")

    assert not [
        envelope.get_event() for envelope in sentry_events if envelope.get_event()
    ]


def test_other_errors_are_still_sent(sentry_events):
    sentry_sdk.capture_exception(ValueError("unexpected application error"))

    events = [
        envelope.get_event() for envelope in sentry_events if envelope.get_event()
    ]
    assert len(events) == 1
    assert events[0]["exception"]["values"][-1]["type"] == "ValueError"


def test_search_spans_are_still_sent(sentry_events):
    with sentry_sdk.start_transaction(name="entity request", op="http.server"):
        with sentry_sdk.start_span(name="entity.search", op="entity.search"):
            sentry_sdk.capture_exception(SqlAlchemyTimeoutError("pool timed out"))

    transactions = [
        envelope.get_transaction_event()
        for envelope in sentry_events
        if envelope.get_transaction_event()
    ]
    assert len(transactions) == 1
    assert transactions[0]["spans"][0]["op"] == "entity.search"
