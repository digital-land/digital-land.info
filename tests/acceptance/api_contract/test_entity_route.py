"""
Module to test the routes that follow /entity. this includes both the get entity and the entity search
"""

import pytest
from application.db.models import EntityOrm

mock_entities = [
    {
        "entity": "106",
        "name": "A space",
        "entry_date": "2019-01-07",
        "start_date": "2019-01-05",
        "end_date": "2020-01-07",
        "dataset": "greenspace",
        "json": None,
        "organisation_entity": None,
        "prefix": "greenspace",
        "reference": "Q1234567",
        "typology": "geography",
        "geometry": "MultiPolygon (((-0.3386878967285156 53.74426323597749, -0.337904691696167 53.743857158459996, -0.33673524856567383 53.744003093019586, -0.33637046813964844 53.74463124033804, -0.3365743160247803 53.74525937826645, -0.33737897872924805 53.74541799747043, -0.33875226974487305 53.74505000000031, -0.3386878967285156 53.74426323597749)))",  # noqa: E501
        "point": "POINT (-0.33737897872924805 53.74541799747043)",
        "quality": "authoritative",
    },
    {
        "entity": "107",
        "name": "A space",
        "entry_date": "2019-01-07",
        "start_date": "2019-01-05",
        "end_date": "2020-01-07",
        "dataset": "greenspace",
        "json": {"local-planning-authority": "E01000001"},
        "organisation_entity": None,
        "prefix": "greenspace",
        "reference": "Q1234568",
        "typology": "geography",
        "geometry": "MultiPolygon (((-0.3386878967285156 53.74426323597749, -0.337904691696167 53.743857158459996, -0.33673524856567383 53.744003093019586, -0.33637046813964844 53.74463124033804, -0.3365743160247803 53.74525937826645, -0.33737897872924805 53.74541799747043, -0.33875226974487305 53.74505000000031, -0.3386878967285156 53.74426323597749)))",  # noqa: E501
        "point": "POINT (-0.33737897872924805 53.74541799747043)",
        "quality": "some",
    },
]

# Get Entity Route (/entity/{entity}.{extension}) Testing
# =======================================================
# Path Parameter Testing
# ----------------------


@pytest.mark.parametrize(
    "extension,expected_headers",
    [
        ("json", "application/json"),
        ("geojson", "application/json"),
    ],
)
def test_entity_extension_json(client, db_session, extension, expected_headers):
    """
    Test the extension path parameter works and givens
    the correct resposne when asking for a json
    """
    # add an entity with the correct_curie
    for entity in mock_entities:
        db_session.add(EntityOrm(**entity))
    db_session.commit()

    if extension:
        endpoint = f"/curie/greenspace:Q1234568.{extension}"
    else:
        endpoint = "/curie/greenspace:Q1234568"

    response = client.get(endpoint)
    headers = response.headers["Content-Type"]

    assert expected_headers in headers, f"Incorrect headers returned: '{headers}'"


# test ONLY correct fiellds ae returned
# ----------------------


def test_entity_fields_returned(client, db_session):
    """
    Test that only the correct fields are returned from an entity request which doesn't use the field parameters
    this can be changed but may affect users so should be deliberate
    """
    # add an entity with the correct_curie
    for entity in mock_entities:
        db_session.add(EntityOrm(**entity))
    db_session.commit()

    endpoint = "/entity/106.json"
    response = client.get(endpoint)
    data = response.json()

    expected_fields = {
        "entity",
        "name",
        "entry-date",
        "start-date",
        "end-date",
        "dataset",
        "organisation-entity",
        "prefix",
        "reference",
        "typology",
        "geometry",
        "point",
        "quality",
    }

    returned_fields = set(data.keys())

    assert (
        expected_fields == returned_fields
    ), f"Expected fields {expected_fields} but got {returned_fields}"
