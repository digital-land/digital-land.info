from functools import lru_cache
from typing import Iterator

from fastapi_utils.session import FastAPISessionMaker
from sqlalchemy.orm import Session

from application.settings import get_settings


def get_db_session() -> Iterator[Session]:
    yield from _get_fastapi_sessionmaker().get_db()


@lru_cache()
def _get_fastapi_sessionmaker() -> FastAPISessionMaker:
    database_uri = get_settings().READ_DATABASE_URL
    return FastAPISessionMaker(database_uri)
