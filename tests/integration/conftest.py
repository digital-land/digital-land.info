import pytest
import alembic
from fastapi import FastAPI

from fastapi.testclient import TestClient
from alembic.config import Config
from sqlalchemy.orm import Session

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dl_web.settings import Settings


# TODO - I don't really want to do this at all really
# it would be better I think to just be driven just off
# of env vars? and in test just use a .env.test over ride?
# so get settings would just return the right thing?
@pytest.fixture(scope="session")
def test_settings() -> Settings:
    from dl_web.settings import get_settings

    settings = get_settings()
    settings.READ_DATABASE_URL = f"{settings.READ_DATABASE_URL}_test"
    settings.WRITE_DATABASE_URL = f"{settings.WRITE_DATABASE_URL}_test"
    return settings


@pytest.fixture(scope="session")
def apply_migrations(test_settings):
    config = Config("alembic.ini")
    alembic.command.upgrade(config, "head")
    yield
    alembic.command.downgrade(config, "base")


@pytest.fixture(scope="session")
def app(apply_migrations) -> FastAPI:
    from dl_web.factory import create_app

    return create_app()


@pytest.fixture(scope="session")
def db_session(app: FastAPI, test_settings: Settings) -> Session:
    engine = create_engine(test_settings.READ_DATABASE_URL)
    db = sessionmaker(bind=engine)()
    yield db
    db.close()
    engine.dispose()


@pytest.fixture(scope="session")
def client(app: FastAPI, test_settings: Settings) -> TestClient:
    return TestClient(app)
