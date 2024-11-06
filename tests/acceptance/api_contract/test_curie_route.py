"""
A python module which holds tests that have to pass for the curie route of
our api. essentially testing the contract with consumers
of the api functionality. Does not focus on looking at html responses
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
    },
    {
        "entity": "107",
        "name": "A space",
        "entry_date": "2019-01-07",
        "start_date": "2019-01-05",
        "end_date": "2020-01-07",
        "dataset": "greenspace",
        "json": None,
        "organisation_entity": None,
        "prefix": "greenspace",
        "reference": "Q1234568",
        "typology": "geography",
        "geometry": "MultiPolygon (((-0.3386878967285156 53.74426323597749, -0.337904691696167 53.743857158459996, -0.33673524856567383 53.744003093019586, -0.33637046813964844 53.74463124033804, -0.3365743160247803 53.74525937826645, -0.33737897872924805 53.74541799747043, -0.33875226974487305 53.74505000000031, -0.3386878967285156 53.74426323597749)))",  # noqa: E501
        "point": "POINT (-0.33737897872924805 53.74541799747043)",
    },
]

# Get Curie Route (/curie/{prefix}:{reference}.{extension}) Testing
# =================================================================
# Path Parameter Testing
# ----------------------


@pytest.mark.parametrize(
    "extension,expected_headers",
    [
        ("json", "application/json"),
        ("geojson", "application/json"),
    ],
)
def test_curie_extension_returns_correct_headers(
    client, db_session, extension, expected_headers
):
    """
    Test the extension path parameter will return the correct type of response
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
