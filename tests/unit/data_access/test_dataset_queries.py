import json
from unittest.mock import MagicMock

import pytest
from redis.exceptions import ConnectionError, TimeoutError

from application.data_access.dataset_queries import get_dataset_names
from application.data_access.digital_land_queries import get_typology_names
from application.db.session import DbSession


@pytest.fixture(params=["dataset", "typology"])
def cached_names(request):
    if request.param == "dataset":
        return get_dataset_names, "cache:dataset-names", 21600
    return get_typology_names, "cache:typology-names", 21600


@pytest.fixture
def db():
    session = MagicMock()
    session.query.return_value.all.return_value = [("listed-building",)]
    session.query.return_value.where.return_value.all.return_value = [
        ("listed-building",)
    ]
    return DbSession(session=session, redis=MagicMock())


@pytest.mark.parametrize("names", [["listed-building"], []])
def test_cache_hit_skips_database(db, names, cached_names):
    lookup, key, _ = cached_names
    db.redis.get.return_value = json.dumps(names)
    assert lookup(db) == names
    db.session.query.assert_not_called()
    db.redis.get.assert_called_once_with(key)


def test_cache_miss_stores_names_with_independent_expiry(db, cached_names):
    lookup, key, ttl = cached_names
    db.redis.get.return_value = None
    assert lookup(db) == ["listed-building"]
    db.redis.setex.assert_called_once_with(key, time=ttl, value='["listed-building"]')


def test_dataset_names_excludes_specification(db):
    db.redis = None
    get_dataset_names(db)
    query = db.session.query.return_value
    predicate = query.where.call_args.args[0]
    assert str(predicate) == "dataset.typology != :typology_1"
    assert predicate.compile().params == {"typology_1": "specification"}


def test_without_redis_uses_database(db, cached_names):
    db.redis = None
    assert cached_names[0](db) == ["listed-building"]


@pytest.mark.parametrize("error", [ConnectionError, TimeoutError])
def test_redis_failure_falls_back_to_database(db, error, cached_names):
    db.redis.get.side_effect = error("unavailable")
    db.redis.setex.side_effect = error("unavailable")
    assert cached_names[0](db) == ["listed-building"]


def test_malformed_cache_is_refreshed(db, cached_names):
    db.redis.get.return_value = "not json"
    assert cached_names[0](db) == ["listed-building"]
    db.redis.setex.assert_called_once()


def test_database_failure_is_not_cached(db, cached_names):
    db.redis.get.return_value = None
    db.session.query.side_effect = RuntimeError("database failed")
    with pytest.raises(RuntimeError, match="database failed"):
        cached_names[0](db)
    db.redis.setex.assert_not_called()
