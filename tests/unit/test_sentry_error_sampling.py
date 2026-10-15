import pytest
from redis.exceptions import TimeoutError as RedisTimeoutError
from sentry_sdk import Client
from sqlalchemy.exc import OperationalError, TimeoutError as PoolTimeoutError

from application.factory import add_middleware, sample_sentry_error


@pytest.mark.parametrize(
    "error",
    [
        TimeoutError("timed out"),
        RedisTimeoutError("timed out"),
        PoolTimeoutError("pool exhausted"),
        OperationalError("SELECT 1", {}, RuntimeError("connection failed")),
    ],
)
def test_previously_ignored_errors_are_sampled(error):
    hint = {"exc_info": (type(error), error, None)}

    assert sample_sentry_error({}, hint) == 0.01


@pytest.mark.parametrize("error", [ValueError("invalid"), RuntimeError("failed")])
def test_other_errors_are_fully_reported(error):
    hint = {"exc_info": (type(error), error, None)}

    assert sample_sentry_error({}, hint) == 1.0


@pytest.mark.parametrize("hint", [{}, {"exc_info": None}])
def test_events_without_exception_information_are_fully_reported(hint):
    assert sample_sentry_error({"message": "an error was logged"}, hint) == 1.0


@pytest.mark.parametrize(
    "error, random_value, expected_events",
    [
        (TimeoutError("timed out"), 0.0, 1),
        (TimeoutError("timed out"), 0.5, 0),
        (OperationalError("SELECT 1", {}, RuntimeError("failed")), 0.0, 1),
        (OperationalError("SELECT 1", {}, RuntimeError("failed")), 0.5, 0),
        (ValueError("invalid"), 0.5, 1),
    ],
)
def test_sdk_sends_sampled_errors_without_network(
    mocker, error, random_value, expected_events
):
    captured = []
    mocker.patch("sentry_sdk.client.random.random", return_value=random_value)
    client = Client(
        dsn="https://public@example.com/1",
        transport=captured.append,
        default_integrations=False,
        auto_enabling_integrations=False,
        error_sampler=sample_sentry_error,
    )
    try:
        client.capture_event(
            {"message": "test error", "level": "error"},
            hint={"exc_info": (type(error), error, None)},
        )
        assert len(captured) == expected_events
    finally:
        client.close()


def test_factory_replaces_ignores_with_sampler(mocker):
    from fastapi import FastAPI

    settings = mocker.Mock(
        SENTRY_DSN="https://public@example.com/1",
        ENVIRONMENT="test",
        SENTRY_TRACE_SAMPLE_RATE=0.01,
        RELEASE_TAG="test-release",
    )
    init = mocker.patch("application.factory.sentry_sdk.init")

    add_middleware(FastAPI(), settings)

    assert init.call_args.kwargs["error_sampler"] is sample_sentry_error
    assert "ignore_errors" not in init.call_args.kwargs
