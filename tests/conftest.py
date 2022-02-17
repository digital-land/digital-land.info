import pytest
import alembic
from fastapi import FastAPI

from fastapi.testclient import TestClient
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from application.db.models import DatasetOrm, EntityOrm
from application.settings import Settings, get_settings


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    from dotenv import load_dotenv

    load_dotenv(".env.test", override=True)
    return get_settings()


@pytest.fixture(scope="session")
def apply_migrations(test_settings):
    config = Config("alembic.ini")
    alembic.command.upgrade(config, "head")
    yield
    alembic.command.downgrade(config, "base")


@pytest.fixture(scope="session")
def db_session(test_settings: Settings) -> Session:
    engine = create_engine(test_settings.READ_DATABASE_URL)
    db = sessionmaker(bind=engine)()
    yield db
    db.close()
    engine.dispose()


@pytest.fixture(scope="session")
def test_data(apply_migrations, db_session: Session):
    from tests.test_data import datasets
    from tests.test_data import entities

    for dataset in datasets:
        themes = dataset.pop("themes").split(",")
        ds = DatasetOrm(**dataset)
        ds.themes = themes
        db_session.add(ds)

    for entity in entities:
        e = EntityOrm(**entity)
        db_session.add(e)

    db_session.commit()


@pytest.fixture(scope="session")
def app(apply_migrations) -> FastAPI:
    from application.factory import create_app

    return create_app()


@pytest.fixture(scope="session")
def client(app: FastAPI, test_settings: Settings) -> TestClient:
    return TestClient(app)


# This is a hack to fix a bug in starlette https://github.com/encode/starlette/issues/472
@pytest.fixture
def exclude_middleware(app):
    user_middleware = app.user_middleware.copy()
    app.user_middleware = []
    app.middleware_stack = app.build_middleware_stack()
    yield
    app.user_middleware = user_middleware
    app.middleware_stack = app.build_middleware_stack()
