from typing import Generator, Dict, List, Union

import pytest
import alembic
from fastapi import FastAPI
from fastapi.testclient import TestClient
from alembic.config import Config
from pydantic import PostgresDsn
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy_utils import database_exists, create_database, drop_database

from application.db.models import (
    DatasetOrm,
    EntityOrm,
    OldEntityOrm,
    LookupOrm,
    AttributionOrm,
    LicenceOrm,
)
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


@pytest.fixture(scope="session")
def create_db(test_settings: Settings) -> PostgresDsn:
    database_url = test_settings.WRITE_DATABASE_URL
    if database_exists(database_url):
        drop_database(database_url)
    create_database(database_url)
    return database_url


@pytest.fixture(scope="session")
def db_session(
    create_db: PostgresDsn, test_settings: Settings
) -> Generator[Session, None, None]:
    engine = create_engine(create_db)
    db = sessionmaker(bind=engine)()
    yield db
    db.close()
    engine.dispose()


@pytest.fixture(scope="session")
def test_data(apply_migrations, db_session: Session):
    from tests.test_data import datasets
    from tests.test_data import entities

    dataset_models = []
    for dataset in datasets:
        themes = dataset.pop("themes").split(",")
        ds = DatasetOrm(**dataset)
        ds.themes = themes

        attribution = dataset.get("attribution", None)
        if attribution and db_session.query(AttributionOrm).get(attribution) is None:
            db_session.add(
                AttributionOrm(attribution=attribution, text="attribution text")
            )

        licence = dataset.get("licence", None)
        if licence and db_session.query(LicenceOrm).get(licence) is None:
            db_session.add(LicenceOrm(licence=licence, text="licence text"))

        db_session.add(ds)
        dataset_models.append(ds)

    entity_models = []
    for i, entity in enumerate(entities):
        e = EntityOrm(**entity)
        db_session.add(e)
        lookup = LookupOrm(
            id=i,
            entity=entity["entity"],
            prefix=entity["prefix"],
            reference=entity["reference"],
        )
        db_session.add(lookup)
        entity_models.append(e)

    db_session.commit()
    return {"datasets": datasets, "entities": entities}


@pytest.fixture(scope="session")
def test_data_old_entities(
    test_data: Dict[str, List[Union[DatasetOrm, EntityOrm]]], db_session: Session
) -> Dict[
    str, Union[List[Union[DatasetOrm, EntityOrm]], Dict[int, List[OldEntityOrm]]]
]:
    dataset_models = [
        db_session.query(DatasetOrm).get(test_datum["dataset"])
        for test_datum in test_data["datasets"]
    ]
    entity_models = [
        db_session.query(EntityOrm).get(test_datum["entity"])
        for test_datum in test_data["entities"]
    ]
    old_entity_redirect = [
        OldEntityOrm(
            old_entity=entity_models[0],
            new_entity=entity_models[0],
            status=301,
            dataset=entity_models[5]
        )
    ]
    db_session.add(old_entity_redirect[0])
    old_entity_gone = [OldEntityOrm(old_entity=entity_models[1], status=410, dataset=entity_models[5])]
    db_session.add(old_entity_gone[0])
    db_session.commit()

    return {
        "datasets": dataset_models,
        "entities": entity_models,
        "old_entities": {
            301: old_entity_redirect,
            410: old_entity_gone,
        },
    }


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
