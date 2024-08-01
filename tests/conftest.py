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
from multiprocessing.context import Process
import uvicorn
import time
import csv
import json
import logging

from application.app import create_app  # noqa: E402

from application.db.models import (
    Base,
    DatasetOrm,
    EntityOrm,
    OldEntityOrm,
    LookupOrm,
    AttributionOrm,
    LicenceOrm,
)
from application.db.session import get_session
from application.settings import Settings, get_settings
from tests.utils.database import (
    add_base_datasets_to_database,
    add_base_typology_to_database,
    add_base_entities_to_database,
    reset_database,
)

DEFAULT_TEST_DATABASE_URL = "postgresql://postgres:postgres@localhost/digital_land_test"


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    from dotenv import load_dotenv

    load_dotenv(override=True)
    get_settings.cache_clear()

    settings = Settings(
        WRITE_DATABASE_URL=DEFAULT_TEST_DATABASE_URL,
        READ_DATABASE_URL=DEFAULT_TEST_DATABASE_URL,
    )

    logging.warning(settings)

    return settings


@pytest.fixture(scope="session")
def create_db(test_settings) -> PostgresDsn:
    # grab db url and create db
    database_url = DEFAULT_TEST_DATABASE_URL
    if database_exists(database_url):
        drop_database(database_url)
    create_database(database_url)
    logging.error(database_url)

    # apply migrations in new db, this assumes we will always want a properly set-up db
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", database_url)
    alembic.command.upgrade(config, "head")

    yield database_url
    drop_database(database_url)


@pytest.fixture(scope="session")
def db_engine(create_db):
    engine = create_engine(create_db)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    connection = db_engine.connect()

    # begin a non-ORM transaction
    transaction = connection.begin()

    # bind an individual Session to the connection
    db_session = sessionmaker(bind=connection)()
    yield db_session

    db_session.close()
    transaction.rollback()
    connection.close()


# TODO dedupe from code below
@pytest.fixture(scope="function")
def test_data(db_session: Session):
    datasets = []
    dataset_models = []
    with open("tests/test_data/datasets.csv") as f:
        dictreader = csv.DictReader(f, delimiter="|")
        for dataset in dictreader:
            dataset = {k: (v if v != "" else None) for k, v in dataset.items()}
            dataset["paint_options"] = json.loads(dataset["paint_options"])
            datasets.append(dataset)
            themes = dataset.pop("themes").split(",")
            ds = DatasetOrm(**dataset)
            ds.themes = themes

            attribution = dataset.get("attribution", None)
            if (
                attribution
                and db_session.query(AttributionOrm).get(attribution) is None
            ):
                db_session.add(
                    AttributionOrm(attribution=attribution, text="attribution text")
                )

            licence = dataset.get("licence", None)
            if licence and db_session.query(LicenceOrm).get(licence) is None:
                db_session.add(LicenceOrm(licence=licence, text="licence text"))

            db_session.add(ds)
            dataset_models.append(ds)

    entities = []
    entity_models = []
    with open("tests/test_data/entities.csv") as f:
        dictreader = csv.DictReader(f, delimiter="|")
        i = 0
        for entity in dictreader:
            entity = {k: (v if v != "" else None) for k, v in entity.items()}
            entities.append(entity)
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
            i += 1

    return {"datasets": datasets, "entities": entities}


@pytest.fixture(scope="function")
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
            dataset="greenspace",
        )
    ]
    db_session.add(old_entity_redirect[0])
    old_entity_gone = [
        OldEntityOrm(old_entity=entity_models[1], status=410, dataset="greenspace")
    ]
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


# Creating a testclient, this can be used for API testing
# you can get html out too but it won't test it in the browser
# just whether a static html is produced, it works with the
# normal db_session
@pytest.fixture(scope="session")
def app(create_db) -> FastAPI:
    from application.factory import create_app

    app = create_app()
    return app


@pytest.fixture(scope="function")
def client(app: FastAPI, db_session: Session) -> TestClient:
    """
    Fixture to be used to get a client which requests can be sent to
    this should be used for api calls does not spin up a local server
    so separate programs e.g. a browser cannot interact with it
    """
    app.dependency_overrides[get_session] = lambda: db_session
    return TestClient(app)


# TODO Can we remove this?
# This is a hack to fix a bug in starlette https://github.com/encode/starlette/issues/472
@pytest.fixture
def exclude_middleware(app):
    user_middleware = app.user_middleware.copy()
    app.user_middleware = []
    app.middleware_stack = app.build_middleware_stack()
    yield
    app.user_middleware = user_middleware
    app.middleware_stack = app.build_middleware_stack()


# TODO Can we remove this?
# this function ensures that a database is empty for a test by...
#   - resets the database
#   - adds the base datasets and typology to the database
#   - yields back to the test
#   - resets the database
@pytest.fixture()
def empty_database():
    reset_database()
    add_base_datasets_to_database()
    add_base_typology_to_database()
    yield
    reset_database()


# TODO Can we remove this?
# this function ensures that a database has only the base elements
#   - resets the database
#   - adds the entities and datasets from tests/test_data/datasets.csv and tests/test_data/entities.csv to the database
#   - yields back to the test
#   - resets the database
@pytest.fixture()
def add_base_entities_to_database_yield_reset():
    reset_database()
    add_base_entities_to_database()
    add_base_datasets_to_database()
    add_base_typology_to_database()
    yield
    reset_database()


@pytest.fixture()
def skip_if_not_supportsGL(page):
    supportsGL = page.evaluate(
        """
        () => {
            const canvas = document.createElement("canvas");
            const gl = canvas.getContext("webgl") || canvas.getContext("experimental-webgl");
            return gl instanceof WebGLRenderingContext;
        }
    """
    )
    if not supportsGL:
        pytest.skip("Test requires WebGL support")


# Testing the Applicaiton in the browser
# this requires us to use playwright and navigate to a local server
# unfortunately we cannot use transaction to control changes to a db
# Instead we manually delete all of the values in the tables between tests
@pytest.fixture(scope="function")
def app_db_session(create_db):
    """
    Yields a db session which can be used to load data for an
    external application
    """
    engine = create_engine(create_db)
    session = sessionmaker(engine)()
    yield session
    for table in Base.metadata.sorted_tables:
        session.execute(table.delete())
    session.commit()
    session.close()
    engine.dispose()


@pytest.fixture(scope="function")
def app_test_data(app_db_session: Session):
    datasets = []
    dataset_models = []
    with open("tests/test_data/datasets.csv") as f:
        dictreader = csv.DictReader(f, delimiter="|")
        for dataset in dictreader:
            dataset = {k: (v if v != "" else None) for k, v in dataset.items()}
            dataset["paint_options"] = json.loads(dataset["paint_options"])
            datasets.append(dataset)
            themes = dataset.pop("themes").split(",")
            ds = DatasetOrm(**dataset)
            ds.themes = themes

            attribution = dataset.get("attribution", None)
            if (
                attribution
                and app_db_session.query(AttributionOrm).get(attribution) is None
            ):
                app_db_session.add(
                    AttributionOrm(attribution=attribution, text="attribution text")
                )

            licence = dataset.get("licence", None)
            if licence and app_db_session.query(LicenceOrm).get(licence) is None:
                app_db_session.add(LicenceOrm(licence=licence, text="licence text"))

            app_db_session.add(ds)
            dataset_models.append(ds)

    entities = []
    entity_models = []
    with open("tests/test_data/entities.csv") as f:
        dictreader = csv.DictReader(f, delimiter="|")
        i = 0
        for entity in dictreader:
            entity = {k: (v if v != "" else None) for k, v in entity.items()}
            entities.append(entity)
            e = EntityOrm(**entity)
            app_db_session.add(e)
            lookup = LookupOrm(
                id=i,
                entity=entity["entity"],
                prefix=entity["prefix"],
                reference=entity["reference"],
            )
            app_db_session.add(lookup)
            entity_models.append(e)
            app_db_session.commit()
            i += 1

    return {"datasets": datasets, "entities": entities}


# in a perfect world this would be a fixture but there were issues with pickling
# to run separate process
def get_context_session_override():
    engine = create_engine(DEFAULT_TEST_DATABASE_URL)
    session = sessionmaker(engine)()
    return session


appInstance = create_app()
appInstance.dependency_overrides[get_session] = get_context_session_override
HOST = "0.0.0.0"
PORT = 9000


def run_server():
    uvicorn.run(appInstance, host=HOST, port=PORT)


def mock_settings() -> Settings:
    from dotenv import load_dotenv

    load_dotenv(override=True)
    get_settings.cache_clear()

    return Settings(
        WRITE_DATABASE_URL=DEFAULT_TEST_DATABASE_URL,
        READ_DATABASE_URL=DEFAULT_TEST_DATABASE_URL,
    )


@pytest.fixture(scope="session")
def server_url(create_db):
    proc = Process(target=run_server, args=(), daemon=True)
    proc.start()
    # Wait for FastAPI to start (optional)
    time.sleep(10)  # Adjust this time as needed for the FastAPI app to fully start

    yield f"http://{HOST}:{PORT}"
    proc.kill()
