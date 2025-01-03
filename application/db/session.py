from functools import lru_cache
from typing import Iterator

from fastapi_utils.session import FastAPISessionMaker
from sqlalchemy.orm import Session

from application.settings import get_settings
import logging

logger = logging.getLogger(__name__)


# this can be used in fast api path functions using Depends to inject a db session
def get_session() -> Iterator[Session]:
    logger.info(
        f"Database engine created with pool_size={get_settings().DB_POOL_SIZE}, "
        f"max_overflow={get_settings().DB_POOL_MAX_OVERFLOW}"
    )
    yield from _get_fastapi_sessionmaker().get_db()


# this can be used in non path functions to create a context manager for a db session
# see https://github.com/dmontagu/fastapi-utils/blob/master/fastapi_utils/session.py#L77:L91
def get_context_session() -> Iterator[Session]:
    return _get_fastapi_sessionmaker().context_session()


@lru_cache()
def _get_fastapi_sessionmaker() -> FastAPISessionMaker:
    database_uri = get_settings().READ_DATABASE_URL
    return FastAPISessionMaker(database_uri)
