import json
from unittest.mock import MagicMock

import pytest
from redis.exceptions import ConnectionError, TimeoutError

from application.data_access.entity_queries import get_dataset_entity_counts
from application.db.session import DbSession


@pytest.fixture
def db():
    session = MagicMock()
    session.execute.return_value.fetchall.return_value = [
        ("ancient-woodland", 10),
        ("brownfield-land", 20),
    ]
    return DbSession(session=session, redis=MagicMock())


@pytest.mark.parametrize("counts", [{"ancient-woodland": 10}, {}])
def test_cached_counts_skip_database(db, counts):
    db.redis.get.return_value = json.dumps(counts)

    assert get_dataset_entity_counts(db) == counts
    db.session.execute.assert_not_called()
    db.redis.get.assert_called_once_with("cache:dataset-entity-counts")


def test_cache_miss_round_trips_counts_with_fifteen_minute_expiry(db):
    db.redis.get.return_value = None
    counts = get_dataset_entity_counts(db)

    assert counts == {"ancient-woodland": 10, "brownfield-land": 20}
    db.redis.setex.assert_called_once_with(
        "cache:dataset-entity-counts", time=900, value=json.dumps(counts)
    )
    db.redis.get.return_value = db.redis.setex.call_args.kwargs["value"]

    assert get_dataset_entity_counts(db) == counts
    db.session.execute.assert_called_once()


def test_counts_refresh_after_expiry(db):
    db.redis.get.return_value = '{"ancient-woodland": 10}'
    assert get_dataset_entity_counts(db) == {"ancient-woodland": 10}

    db.redis.get.return_value = None
    db.session.execute.return_value.fetchall.return_value = [("ancient-woodland", 11)]
    assert get_dataset_entity_counts(db) == {"ancient-woodland": 11}
    db.redis.setex.assert_called_once()


def test_counts_without_redis_use_database(db):
    db.redis = None

    assert get_dataset_entity_counts(db) == {
        "ancient-woodland": 10,
        "brownfield-land": 20,
    }


@pytest.mark.parametrize("error", [ConnectionError, TimeoutError])
def test_redis_failure_falls_back_to_database(db, error):
    db.redis.get.side_effect = error("unavailable")
    db.redis.setex.side_effect = error("unavailable")

    assert get_dataset_entity_counts(db) == {
        "ancient-woodland": 10,
        "brownfield-land": 20,
    }


def test_malformed_cache_is_refreshed(db):
    db.redis.get.return_value = "not json"

    assert get_dataset_entity_counts(db)["ancient-woodland"] == 10
    db.redis.setex.assert_called_once()


def test_database_failure_is_not_cached(db):
    db.redis.get.return_value = None
    db.session.execute.side_effect = RuntimeError("database failed")

    with pytest.raises(RuntimeError, match="database failed"):
        get_dataset_entity_counts(db)
    db.redis.setex.assert_not_called()
