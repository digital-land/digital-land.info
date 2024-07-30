import pytest
import requests


@pytest.mark.parametrize(
    "exclude_field, expected_fields",
    [
        (
            ["geometry"],
            {
                "entry-date",
                "start-date",
                "entity",
                "dataset",
                "typology",
                "reference",
                "prefix",
                "organisation-entity",
                "point",
                "notes",
            },
        ),
        (
            ["point", "geometry"],
            {
                "entry-date",
                "start-date",
                "entity",
                "dataset",
                "typology",
                "reference",
                "prefix",
                "organisation-entity",
                "notes",
            },
        ),
    ],
)
def test_get_entity_json_exclude_field(server_url, exclude_field, expected_fields):
    params = {"exclude_field": ",".join(exclude_field)} if exclude_field else {}
    response = requests.get(f"{server_url}/entity.json", params=params)

    response_json = response.json()
    entities = response_json.get("entities", [])

    assert isinstance(entities, list), "Expected 'entities' to be a list"

    for entity in entities:
        for field in expected_fields:
            assert (
                field in entity
            ), f"Expected field '{field}' not found in entity: {entity}"
        for field in exclude_field:
            assert (
                field not in entity
            ), f"Field '{field}' should not be in entity: {entity}"


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
            "notes",
        }
    ],
)
def test_get_entity_json_no_exclude_field(server_url, expected_fields):
    response = requests.get(f"{server_url}/entity.json")
    assert response.status_code == 200

    response_json = response.json()
    entities = response_json.get("entities", [])
    assert isinstance(entities, list), "Expected 'entities' to be a list"
    for entity in entities:
        for field in expected_fields:
            assert (
                field in entity
            ), f"Expected field '{field}' not found in entity: {entity}"
