from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Iterator
import logging
from application.settings import get_settings
from contextlib import contextmanager
from functools import wraps
from datetime import datetime

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
# Set up logging
logger = logging.getLogger(__name__)


def _create_engine():
    settings = get_settings()
    engine = create_engine(
        settings.READ_DATABASE_URL,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_POOL_MAX_OVERFLOW,
    )

    logger.info(
        f"Engine created with pool_size={engine.pool.size()}, "
        f"max_overflow={engine.pool._max_overflow} "
    )

    return engine


# Create session factory
engine = _create_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_context_session() -> Iterator[Session]:
    session = SessionLocal()
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
