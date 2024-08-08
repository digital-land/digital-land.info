import pytest
from application.db.models import EntityOrm


@pytest.mark.parametrize(
    "exclude",
    [["organisation-entity"], ["entry-date", "prefix"]],
)
def test_entity_search_exclude_field_for_json_response(
    client,
    db_session,
    test_data: dict,
    exclude: list,
):
    # Clear the table to avoid duplicates
    db_session.query(EntityOrm).delete()
    db_session.commit()

    # Load entities into the database
    for entity_data in test_data["entities"]:
        db_session.add(EntityOrm(**entity_data))
    db_session.commit()

    params = {"exclude_field": ",".join(exclude)} if exclude else {}
    response = client.get("/entity.json", params=params)
    response_json = response.json()
    entities = response_json.get("entities", [])

    assert (
        len(entities) > 0
    ), "No entities being returned so cannot check that the fields are correct"
    assert isinstance(entities, list), "Expected 'entities' to be a list"

    for entity in entities:
        # Check if excluded fields are not present
        for field in exclude:
            assert (
                field not in entity
            ), f"Field '{field}' should not be in entity: {entity}"


@pytest.mark.parametrize(
    "expected_fields",
    [
        {
            "entry-date": "2019-01-07",
            "start-date": "2019-01-05",
            "end-date": "2020-01-07",
            "entity": "106",
            "name": "A space",
            "dataset": "greenspace",
            "typology": "geography",
            "reference": "Q1234567",
            "prefix": "greenspace",
            "geometry": "MultiPolygon (((-0.3386878967285156 53.74426323597749, -0.337904691696167 53.743857158459996, -0.33673524856567383 53.744003093019586, -0.33637046813964844 53.74463124033804, -0.3365743160247803 53.74525937826645, -0.33737897872924805 53.74541799747043, -0.33875226974487305 53.74505000000031, -0.3386878967285156 53.74426323597749)))",  # noqa: E501
            "point": "POINT (-0.33737897872924805 53.74541799747043)",
        }
    ],
)
def test_entity_search_no_exclude_field_for_json_response(
    client,
    db_session,
    test_data: dict,
    expected_fields: set,
):
    db_session.query(EntityOrm).delete()
    db_session.commit()
    # Load entities into the database
    for entity_data in test_data["entities"]:
        db_session.add(EntityOrm(**entity_data))
        db_session.commit()

    response = client.get("/entity.json")
    assert response.status_code == 200

    response_json = response.json()
    entities = response_json.get("entities", [])

    assert (
        len(entities) > 0
    ), "No entities being returned so cannot check that the fields are correct"
    assert isinstance(entities, list), "Expected 'entities' to be a list"

    for entity in entities:
        for field in expected_fields:
            assert (
                field in entity
            ), f"Expected field '{field}' not found in entity: {entity}"


@pytest.mark.parametrize("exclude", [["notes"], ["geometry", "notes"]])
def test_entity_search_exclude_field_for_geojson_response(
    client, db_session, test_data: dict, exclude: list
):
    db_session.query(EntityOrm).delete()
    db_session.commit()
    # Load entities into the database
    for feature_properties in test_data["entities"]:
        db_session.add(EntityOrm(**feature_properties))
        db_session.commit()

    # Make the request with the exclude parameters
    params = {"exclude": ",".join(exclude)} if exclude else {}
    response = client.get("/entity.geojson", params=params)
    response_json = response.json()
    assert (
        len(response_json) > 0
    ), "No entities being returned so cannot check that the fields are correct"
    assert "type" in response_json
    assert "features" in response_json

    entities = response_json["features"]
    assert isinstance(entities, list), "Expected 'features' to be a list"

    # Check each feature
    for feature in entities:
        properties = feature.get("properties", {})
        for field in exclude:
            assert (
                field not in properties
            ), f"Property '{field}' should not be in feature properties: {properties}"


@pytest.mark.parametrize(
    "expected_properties",
    [
        {
            "entry-date": "2019-01-07",
            "start-date": "2019-01-05",
            "end-date": "2020-01-07",
            "entity": "106",
            "name": "A space",
            "dataset": "greenspace",
            "typology": "geography",
            "reference": "Q1234567",
            "prefix": "greenspace",
        },
    ],
)
def test_entity_search_no_exclude_field_for_geojson_response(
    client,
    db_session,
    test_data: dict,
    expected_properties: set,
):
    db_session.query(EntityOrm).delete()
    db_session.commit()
    # Load entities into the database
    for feature_properties in test_data["entities"]:
        db_session.add(EntityOrm(**feature_properties))
        db_session.commit()

    response = client.get("/entity.geojson")
    response_json = response.json()
    assert len(response_json) > 0

    entities = response_json["features"]
    assert isinstance(entities, list), "Expected 'features' to be a list"

    # Check each feature
    for feature in entities:
        properties = feature.get("properties", {})
        for field in expected_properties:
            assert (
                field in properties
            ), f"Expected property '{field}'not  found in feature properties: {properties}"
