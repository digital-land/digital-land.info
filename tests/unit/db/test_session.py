import application.db.session as session
from datetime import timedelta


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
