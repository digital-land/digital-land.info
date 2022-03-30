from copy import deepcopy
from csv import DictReader
from io import StringIO

from tests.test_data import datasets
from tests.test_data.wkt_data import (
    random_location_lambeth,
    intersects_with_greenspace_entity,
)


def _transform_dataset_fixture_to_response(datasets):

    for dataset in datasets:
        dataset["prefix"] = dataset["prefix"] or ""
        dataset["start-date"] = dataset.pop("start_date") or ""
        dataset["end-date"] = dataset.pop("end_date") or ""
        dataset["text"] = dataset["text"] or ""
        dataset["entry-date"] = dataset.pop("entry_date") or ""
        dataset["paint-options"] = dataset.pop("paint_options") or ""
        dataset.pop("key_field")
    return datasets


def test_app_returns_valid_geojson_list(client):

    response = client.get("/entity.geojson", headers={"Origin": "localhost"})
    data = response.json()
    assert "type" in data
    assert "features" in data
    assert "FeatureCollection" == data["type"]
    assert [] == data["features"]


def test_lasso_geo_search_finds_results(client, test_data):
    params = {
        "geometry_relation": "intersects",
        "geometry": intersects_with_greenspace_entity,
    }
    response = client.get("/entity.geojson", params=params)
    assert response.status_code == 200
    data = response.json()
    assert "type" in data
    assert "features" in data
    assert "FeatureCollection" == data["type"]
    assert data["features"]

    for feature in data["features"]:
        assert "geometry" in feature
        assert "type" in feature
        assert "Feature" == feature["type"]
        assert "properties" in feature
        assert "greenspace" == feature["properties"]["dataset"]


def test_lasso_geo_search_finds_no_results(client):
    params = {"geometry_relation": "intersects", "geometry": random_location_lambeth}
    response = client.get("/entity.geojson", params=params)
    assert response.status_code == 200
    data = response.json()
    assert "type" in data
    assert "features" in data
    assert "FeatureCollection" == data["type"]
    assert [] == data["features"]


def test_dataset_json_endpoint_returns_as_expected(client):
    response = client.get("/dataset.json")
    assert response.status_code == 200
    data = response.json()
    assert "datasets" in data
    # TODO find way of generating these field values from fixtures
    for dataset in data["datasets"]:
        assert dataset.pop("themes")
        assert dataset.pop("entity-count")
        assert "entities" in dataset
        dataset.pop("entities")

    assert sorted(data["datasets"], key=lambda x: x["name"]) == sorted(
        _transform_dataset_fixture_to_response(deepcopy(datasets)),
        key=lambda x: x["name"],
    )


def test_get_dataset_endpoint_returns_as_expected(client, exclude_middleware):
    """
    Tests that we handle the case of no DatasetCollectionOrm result found gracefully
    """
    response = client.get("/dataset/waste-authority")
    assert response.status_code == 200


def test_get_entity_csv_endpoint_returns_as_expected(
    test_data, client, exclude_middleware, test_data_csv_response
):
    """
    Tests that we return a CSV representation of the test data
    """
    response = client.get("/entity.csv")
    assert response.status_code == 200
    assert response.headers.get("content-type") == "application/csv"
    response_text = response.text
    # Assert hoisted fields present on multiple rows only included once
    assert "foo,foo," not in response_text
    assert "\r\n" in response_text
    with test_data_csv_response.open() as expected_response_file:
        expected_response = list(DictReader(expected_response_file))
    response_dict = list(DictReader(StringIO(response_text)))
    assert "json" not in response_dict[0].keys()
    for row in response_dict:
        row.pop("geojson")
    for row in expected_response:
        row.pop("geojson")
    assert list(response_dict) == list(expected_response)
