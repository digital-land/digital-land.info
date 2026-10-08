import json
from types import SimpleNamespace

import pytest
from redis.exceptions import ConnectionError
from sqlalchemy.exc import OperationalError
from fastapi import HTTPException

from application.data_access.entity_queries import (
    get_entity_count,
    EntityCountCacheBusy,
)
from application.routers.dataset import _get_cached_entity_count


@pytest.fixture
def cache(mocker):
    client = mocker.MagicMock()
    client.get.return_value = None
    client.lock.return_value.acquire.return_value = True
    mocker.patch(
        "application.data_access.entity_queries.get_redis", return_value=client
    )
    mocker.patch(
        "application.data_access.entity_queries.get_settings",
        return_value=SimpleNamespace(DB_STATEMENT_TIMEOUT_MS=600000),
    )
    return client


@pytest.mark.parametrize("counts", [[["title-boundary", 42]], []])
def test_cache_hit_avoids_database(mocker, cache, counts):
    cache.get.return_value = json.dumps(counts)
    session = mocker.MagicMock()
    assert get_entity_count(session) == [tuple(row) for row in counts]
    session.execute.assert_not_called()
    cache.lock.assert_not_called()


def test_cache_fill_and_normalised_selection(mocker, cache):
    session = mocker.MagicMock()
    session.execute.return_value.fetchall.return_value = [("a", 12), ("b", 3)]
    get_entity_count(session, datasets=["b", "a", "a"])
    first_key = cache.setex.call_args.args[0]
    assert cache.setex.call_args.args[1:] == (21600, '[["a", 12], ["b", 3]]')
    cache.lock.return_value.release.assert_called_once()
    get_entity_count(session, datasets=["a", "b"])
    assert cache.setex.call_args.args[0] == first_key
    get_entity_count(session)
    assert cache.setex.call_args.args[0] != first_key
    get_entity_count(session, datasets=[])
    assert cache.setex.call_args.args[0] != first_key


def test_busy_fill_avoids_duplicate_scan(mocker, cache):
    cache.lock.return_value.acquire.return_value = False
    session = mocker.MagicMock()
    with pytest.raises(EntityCountCacheBusy):
        get_entity_count(session)
    session.execute.assert_not_called()
    cache.lock.return_value.release.assert_not_called()


@pytest.mark.parametrize("acquired", [True, False])
def test_rechecks_cache_after_lock_attempt(mocker, cache, acquired):
    cache.lock.return_value.acquire.return_value = acquired
    cache.get.side_effect = [None, '[["a", 10]]']
    session = mocker.MagicMock()
    assert get_entity_count(session) == [("a", 10)]
    session.execute.assert_not_called()


@pytest.mark.parametrize("cached", ["broken", "{}", '[["a", "wrong"]]'])
def test_invalid_cache_is_replaced(mocker, cache, cached):
    cache.get.return_value = cached
    session = mocker.MagicMock()
    session.execute.return_value.fetchall.return_value = [("a", 2)]
    assert get_entity_count(session) == [("a", 2)]
    cache.setex.assert_called_once()


@pytest.mark.parametrize("operation", ["get", "acquire", "setex", "release"])
def test_redis_failure_falls_back_to_database(mocker, cache, operation):
    target = (
        getattr(cache.lock.return_value, operation)
        if operation in ("acquire", "release")
        else getattr(cache, operation)
    )
    target.side_effect = ConnectionError("unavailable")
    session = mocker.MagicMock()
    session.execute.return_value.fetchall.return_value = [("a", 2)]
    assert get_entity_count(session) == [("a", 2)]


def test_database_failure_releases_lock_without_caching(mocker, cache):
    session = mocker.MagicMock()
    session.execute.side_effect = OperationalError("count", {}, Exception("timeout"))
    with pytest.raises(OperationalError):
        get_entity_count(session)
    cache.setex.assert_not_called()
    cache.lock.return_value.release.assert_called_once()


def test_busy_cache_returns_retryable_response(mocker):
    mocker.patch(
        "application.routers.dataset.get_entity_count", side_effect=EntityCountCacheBusy
    )
    with pytest.raises(HTTPException) as error:
        _get_cached_entity_count(mocker.MagicMock())
    assert error.value.status_code == 503
    assert error.value.headers == {"Retry-After": "30"}
