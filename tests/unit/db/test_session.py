import application.db.session as session
from datetime import timedelta
import json
from unittest.mock import MagicMock

from application.core.models import DatasetModel


def test__session_cache():
    cache = {}

    @session.session_cache("key-1", ttl_seconds=10, cache=cache)
    def cached_fn(obj):
        if obj == "A":
            return 1
        return 2

    assert cached_fn("A") == 1
    assert cached_fn("A") == 1
    assert len(cache) == 1

    assert cached_fn("B") == 1
    assert len(cache) == 1

    # force cache expiry
    for entry in cache.values():
        entry.added_at += timedelta(seconds=-11)

    assert cached_fn("B") == 2
    assert len(cache) == 1


def test_redis_cache_preserves_model_round_trip():
    db = session.DbSession(session=MagicMock(), redis=MagicMock())
    model = DatasetModel(dataset="listed-building")
    loader = MagicMock(return_value=[model])
    cached = session.redis_cache("test-models", model_class=DatasetModel)(loader)
    db.redis.get.return_value = None
    assert cached(db) == [model]
    stored = db.redis.setex.call_args.kwargs["value"]
    assert json.loads(stored)[0]["dataset"] == "listed-building"
    db.redis.get.return_value = stored
    assert cached(db) == [model]
    loader.assert_called_once_with(db)


def test__create_engine_applies_statement_timeout(mocker):
    settings = mocker.Mock(
        READ_DATABASE_URL="postgresql://u:p@localhost/db",
        DB_POOL_SIZE=5,
        DB_POOL_MAX_OVERFLOW=10,
        DB_STATEMENT_TIMEOUT_MS=120000,
        ENVIRONMENT="test",
    )
    mocker.patch.object(session, "get_settings", return_value=settings)
    create_engine = mocker.patch.object(session, "create_engine")

    session._create_engine()

    connect_args = create_engine.call_args.kwargs["connect_args"]
    assert connect_args["options"] == "-c statement_timeout=120000"
    assert connect_args["application_name"] == "digital-land.info-test"
