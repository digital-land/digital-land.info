from copy import deepcopy
from csv import DictWriter
from typing import Dict

import pytest
import alembic
from fastapi import FastAPI
from fastapi.testclient import TestClient
from alembic.config import Config
from pydantic import PostgresDsn
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy_utils import database_exists, create_database, drop_database

from application.db.models import DatasetOrm, EntityOrm
from application.settings import Settings, get_settings


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    from dotenv import load_dotenv

    load_dotenv(".env.test", override=True)
    get_settings.cache_clear()
    return get_settings()


@pytest.fixture(scope="session")
def apply_migrations(db_session, test_settings: Settings):
    config = Config("alembic.ini")

    config.set_section_option(
        "alembic", "sqlalchemy.url", test_settings.WRITE_DATABASE_URL
    )

    alembic.command.upgrade(config, "head")
    yield
    alembic.command.downgrade(config, "base")


@pytest.fixture(scope="session")
def create_db(test_settings: Settings):
    database_url = test_settings.WRITE_DATABASE_URL
    if database_exists(database_url):
        drop_database(database_url)
    create_database(database_url)
    return database_url


@pytest.fixture(scope="session")
def db_session(create_db: PostgresDsn, test_settings: Settings) -> Session:
    engine = create_engine(create_db)
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
    return {"dataset": datasets, "entity": entities}


@pytest.fixture
def test_data_csv_response(test_data: Dict[str, list], tmp_path) -> str:
    csv_path = tmp_path.joinpath("test_data_json_hoisted.csv")
    fields = set()
    test_data = deepcopy(test_data)
    for test_datum in test_data["entity"]:
        test_datum.update(test_datum.pop("json") or {})
        fields.update(set(test_datum.keys()))
    with csv_path.open("w+") as csv_file:
        writer = DictWriter(csv_file, fieldnames=fields)
        writer.writeheader()
        for row in test_data["entity"]:
            writer.writerow(row)
    return csv_path


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
