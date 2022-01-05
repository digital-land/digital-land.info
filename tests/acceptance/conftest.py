import pytest
import alembic
from fastapi import FastAPI

from fastapi.testclient import TestClient
from alembic.config import Config
from sqlalchemy.orm import Session

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from application.db.models import Dataset
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
def app(apply_migrations) -> FastAPI:
    from application.factory import create_app

    return create_app()


@pytest.fixture(scope="session")
def db_session(app: FastAPI, test_settings: Settings) -> Session:
    engine = create_engine(test_settings.READ_DATABASE_URL)
    db = sessionmaker(bind=engine)()
    yield db
    db.close()
    engine.dispose()


@pytest.fixture(scope="session")
def data(db_session: Session):
    dataset = Dataset(dataset="test")
    db_session.add(dataset)
    db_session.commit()


@pytest.fixture(scope="session")
def client(app: FastAPI, test_settings: Settings) -> TestClient:
    return TestClient(app)
