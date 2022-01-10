import pytest
import alembic
from fastapi import FastAPI

from fastapi.testclient import TestClient
from alembic.config import Config

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
def app() -> FastAPI:
    from application.factory import create_app

    return create_app()


@pytest.fixture(scope="session")
def client(app: FastAPI, test_settings: Settings) -> TestClient:
    return TestClient(app)
