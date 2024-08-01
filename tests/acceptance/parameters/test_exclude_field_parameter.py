import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from application.db.models import EntityOrm


@pytest.mark.parametrize(
    "exclude, expected_fields",
    [
        (
            ["organisation-entity"],
            {
                "entry-date",
                "start-date",
                "end-date",
                "entity",
                "name",
                "dataset",
                "typology",
                "reference",
                "prefix",
                "point",
            },
        ),
        (
            ["entry-date", "prefix"],
            {
                "start-date",
                "end-date",
                "entity",
                "name",
                "dataset",
                "typology",
                "reference",
                "organisation-entity",
                "point",
            },
        ),
    ],
)
def test_entity_search_exclude_field_for_json_response(
    app_test_data: dict,
    client: TestClient,
    app_db_session: Session,
    exclude: list,
    expected_fields: set,
):
    params = {"exclude_field": ",".join(exclude)} if exclude else {}

    # Clear existing data
    app_db_session.query(EntityOrm).delete()
    app_db_session.commit()

    # Load entities into the database
    for entity_data in app_test_data["entities"]:
        app_db_session.add(EntityOrm(**entity_data))
        app_db_session.commit()

    response = client.get("/entity.json", params=params)
    response_json = response.json()
    entities = response_json.get("entities", [])

    assert isinstance(entities, list), "Expected 'entities' to be a list"

    for entity in entities:
        # Check if excluded fields are not present
        for field in exclude:
            assert (
                field not in entity
            ), f"Field '{field}' should not be in entity: {entity}"

        # Check if expected fields are present
        for field in expected_fields:
            assert (
                field in entity
            ), f"Expected field '{field}' not found in entity: {entity}"


@pytest.mark.parametrize(
    "expected_fields",
    [
        {
            "entry-date",
            "start-date",
            "entity",
            "dataset",
            "typology",
            "reference",
            "prefix",
            "organisation-entity",
            "geometry",
            "point",
        }
    ],
)
def test_entity_search_no_exclude_field_for_json_response(
    app_test_data: dict,
    client: TestClient,
    app_db_session: Session,
    expected_fields: set,
):
    app_db_session.query(EntityOrm).delete()
    app_db_session.commit()
    # Load entities into the database
    for entity_data in app_test_data["entities"]:
        app_db_session.add(EntityOrm(**entity_data))
        app_db_session.commit()

    response = client.get("/entity.json")
    assert response.status_code == 200

    response_json = response.json()
    entities = response_json.get("entities", [])
    assert isinstance(entities, list), "Expected 'entities' to be a list"
    assert (
        len(entities) > 0
    ), "No entities being returned so cannot check that the fields are correct"
    for entity in entities:
        for field in expected_fields:
            assert (
                field in entity
            ), f"Expected field '{field}' not found in entity: {entity}"


@pytest.mark.parametrize(
    "exclude, expected_properties",
    [
        (
            ["notes"],
            {
                "entry-date",
                "start-date",
                "end-date",
                "entity",
                "name",
                "dataset",
                "typology",
                "reference",
                "prefix",
                "organisation-entity",
            },
        ),
        (
            ["prefix", "notes"],
            {
                "entry-date",
                "start-date",
                "end-date",
                "entity",
                "name",
                "dataset",
                "typology",
                "reference",
                "organisation-entity",
            },
        ),
    ],
)
def test_entity_search_exclude_field_for_geojson_response(
    app_test_data: dict,
    client: TestClient,
    app_db_session: Session,
    exclude: list,
    expected_properties: set,
):
    app_db_session.query(EntityOrm).delete()
    app_db_session.commit()
    # Load entities into the database
    for feature_properties in app_test_data["entities"]:
        app_db_session.add(EntityOrm(**feature_properties))
        app_db_session.commit()

    # Make the request with the exclude parameters
    params = {"exclude": ",".join(exclude)} if exclude else {}
    response = client.get("/entity.geojson", params=params)
    response_json = response.json()
    entities = response_json.get("entities", [])
    assert isinstance(entities, list), "Expected 'features' to be a list"

    # Check each feature
    for feature in entities:
        properties = feature.get("properties", {})
        for field in exclude:
            assert (
                field not in properties
            ), f"Property '{field}' should not be in feature properties: {properties}"
        for field in expected_properties:
            assert (
                field in properties
            ), f"Expected property '{field}' not found in feature properties: {properties}"


@pytest.mark.parametrize(
    "expected_properties",
    [
        (
            {
                "entry-date",
                "start-date",
                "end-date",
                "entity",
                "name",
                "dataset",
                "typology",
                "reference",
                "prefix",
                "organisation-entity",
                "notes",
            },
        )
    ],
)
def test_entity_search_no_exclude_field_for_geojson_response(
    app_test_data: dict,
    client: TestClient,
    app_db_session: Session,
    expected_properties: set,
):
    app_db_session.query(EntityOrm).delete()
    app_db_session.commit()
    # Load entities into the database
    for feature_properties in app_test_data["entities"]:
        app_db_session.add(EntityOrm(**feature_properties))
        app_db_session.commit()

    response = client.get("/entity.geojson")
    response_json = response.json()
    entities = response_json.get("entities", [])
    assert isinstance(entities, list), "Expected 'features' to be a list"

    # Check each feature
    for feature in entities:
        properties = feature.get("properties", {})
        for field in expected_properties:
            assert (
                field in properties
            ), f"Expected property '{field}'not  found in feature properties: {properties}"
