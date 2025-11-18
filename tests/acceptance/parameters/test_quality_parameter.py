"""Module to test that the quality parameter is working as expected"""

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


@pytest.mark.parametrize(
    "quality,expected_count",
    [(["some"], 1), (["some", "authoritative"], 2)],
)
def test_quality_filters_rows(client, db_session, quality, expected_count):
    """
    Test that the quality parameter correctly filters entities by quality value.
    """
    # add an entity with the correct_curie
    for entity in mock_entities:
        db_session.add(EntityOrm(**entity))
    db_session.commit()

    query_filters = "&".join([f"quality={quality_value}" for quality_value in quality])
    endpoint = f"/entity.json?{query_filters}"
    response = client.get(endpoint)
    data = response.json()

    assert (
        data["count"] == expected_count
    ), f"Expected {expected_count} entities but got {data['count']}"
