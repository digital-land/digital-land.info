"""
Module to test  how we anticipate the exclude_field parameter. This parameter was primarily
requested so  that larger  unnessary  fields can be excluded (mainly geometry but will apply
to others too). although the field parameter can be used it rwquires  you to know the specific
fields for every dataset. This allows you to still get those but always exclude a field

We do not expect the exclude field to have any effect on the html so we use  test client instead
of server url for testing as it's easier and more efficient.
"""

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
def test_entity_search_excludes_field_for_json_response(
    client, db_session, exclude_field, expected_fields
):
    """
    When searching across entities can we remove fields form the entities using the exclude_fields
    parameter
    """
    params = {"exclude_field": ",".join(exclude_field)} if exclude_field else {}

    # TODO entities need loading into the databse use the db_session to add data

    # TODO change below to using a Fast API test client instead
    response = requests.get(f"{client}/entity.json", params=params)

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
def test_get_entity_json_no_exclude_field(client, db_session, expected_fields):
    # TODO entities need loading into the databse use the db_session to add data

    # TODO change below to using a Fast API test client instead
    response = requests.get(f"{client}/entity.json")
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
