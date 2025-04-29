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
