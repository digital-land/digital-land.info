from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Iterator
import logging
from application.settings import get_settings
from contextlib import contextmanager

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
