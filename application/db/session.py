from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Iterator, Optional
import logging
import json
from application.settings import get_settings, Settings
from contextlib import contextmanager
from functools import wraps, lru_cache
from datetime import datetime
from dataclasses import dataclass

import redis

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
# Set up logging
logger = logging.getLogger(__name__)


def _create_engine():
    settings = get_settings()
    engine = create_engine(
        str(settings.READ_DATABASE_URL),
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_POOL_MAX_OVERFLOW,
        pool_pre_ping=True,
    )

    logger.info(
        f"Engine created with pool_size={engine.pool.size()}, "
        f"max_overflow={engine.pool._max_overflow} "
    )

    return engine


@lru_cache(maxsize=1)
def _get_session_local():
    # Lazily initialised on first request rather than at import time.
    # This avoids calling get_settings() before env vars are available (e.g.
    # during testing), and prevents connection pool corruption when gunicorn
    # forks worker processes — each worker creates its own pool after forking
    # rather than inheriting shared connections from the master process.
    #
    # Use _get_session_local.cache_clear() to force re-initialisation
    # (e.g. in tests that need a fresh engine).
    engine = _create_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session() -> Iterator[Session]:
    db = _get_session_local()()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_context_session() -> Iterator[Session]:
    session = _get_session_local()()
    try:
        yield session
    finally:
        session.close()


class CacheEntry:
    def __init__(self, val):
        self.value = val
        self.added_at = datetime.now()

    def is_expired(self, ttl_seconds):
        now = datetime.now()
        dt = now - self.added_at
        return dt.total_seconds() > ttl_seconds


SESSION_CACHE = {}


def session_cache(key, ttl_seconds=60 * 60, *, cache=SESSION_CACHE):
    def make_key(session):
        return key

    def decorator(user_func):
        @wraps(user_func)
        def wrapper(session):
            cache_key = make_key(session)
            entry = cache.get(cache_key)
            if entry is None or entry.is_expired(ttl_seconds):
                val = user_func(session)
                entry = CacheEntry(val)
                cache[cache_key] = entry
                logger.info(f"session_cache miss for {key}, cache size: {len(cache)}")
            return entry.value

        return wrapper

    return decorator


@dataclass
class DbSession:
    """A way to package DB and Redis sessions/connections as one param."""

    session: Session
    redis: Optional[redis.Redis]


_redis = None


def init_redis(settings: Settings):
    """Initialise Redis instance."""
    global _redis

    try:
        _redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            ssl=settings.REDIS_SECURE,
            decode_responses=True,
            socket_timeout=2,
        )
        _redis.ping()
        logger.info("get_redis(): connected")
    except redis.exceptions.ConnectionError as redis_ex:
        logger.warning(f"get_redis(): failed to connect to redis {redis_ex}")
    except Exception as ex:
        logger.warning("get_redis(): Redis instance creation failed", ex)


def get_redis() -> Iterator[redis.Redis]:
    return _redis


def redis_cache(key, model_class, ttl_seconds=60 * 60 * 6):
    def make_key(session):
        return f"cache:{key}"

    def decorator(user_func):
        @wraps(user_func)
        def wrapper(session: DbSession):
            key = make_key(session)
            if session.redis is None:
                return user_func(session)

            val = None
            try:
                cached = session.redis.get(key)
                if cached is not None:
                    items = json.loads(cached)  # TODO: try without "decode" option
                    val = [model_class.parse_obj(obj) for obj in items]
            except redis.exceptions.ConnectionError as redis_ex:
                logger.warning(f"redis_cache(): redis connection error: {redis_ex}")
            except Exception as ex:
                logger.warning(
                    f"redis_cache(): Failed to get data from cache for key='{key}'", ex
                )

            if val is None:
                val = user_func(session)
                logger.info(f"redis_cache(): session cache miss for key='{key}'")
                try:
                    serialised = json.dumps(
                        [obj.model_dump(mode="json") for obj in val]
                    )
                    session.redis.setex(key, time=ttl_seconds, value=serialised)
                except redis.exceptions.ConnectionError as redis_ex:
                    logger.warning(
                        f"redis_cache(): redis connection error, key='{key}': {redis_ex}"
                    )
                except Exception as ex:
                    logger.warning(
                        f"redis_cache(): Failed to set data for key='{key}'", ex
                    )
            return val

        return wrapper

    return decorator
