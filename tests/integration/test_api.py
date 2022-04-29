from copy import deepcopy

from tests.test_data import datasets
from tests.test_data.wkt_data import (
    random_location_lambeth,
    intersects_with_greenspace_entity,
)


def _transform_dataset_fixture_to_response(datasets, is_geojson=False):

    for dataset in datasets:
        _transform_dataset_to_response(dataset)
    return datasets


def _transform_dataset_to_response(dataset, is_geojson=False):
    dataset["prefix"] = dataset["prefix"] or ""
    dataset["start-date"] = dataset.pop("start_date") or ""
    dataset["end-date"] = dataset.pop("end_date") or ""
    dataset["entry-date"] = dataset.pop("entry_date") or ""
    dataset["name"] = dataset.pop("name") or ""
    if is_geojson:
        dataset["organisation-entity"] = dataset.pop("organisation_entity") or ""
        dataset["entity"] = int(dataset["entity"])
        dataset.pop("geojson")
        dataset.pop("geometry")
        dataset.pop("json")
        dataset.pop("point")
    else:
        dataset["text"] = dataset["text"] or ""
        dataset["paint-options"] = dataset.pop("paint_options") or ""
        dataset.pop("key_field")
    return dataset


def test_app_returns_valid_geojson_list(client):

    response = client.get("/entity.geojson", headers={"Origin": "localhost"})
    data = response.json()
    assert "type" in data
    assert "features" in data
    assert "FeatureCollection" == data["type"]
    assert [] == data["features"]


def test_app_returns_valid_populated_geojson_list(client, test_data):
    expected_response = []
    for entity in test_data["entities"]:
        geojson_dict = entity["geojson"]
        if geojson_dict:
            geojson_dict["properties"] = _transform_dataset_to_response(
                entity, is_geojson=True
            )
            expected_response.append(geojson_dict)
    response = client.get("/entity.geojson", headers={"Origin": "localhost"})
    data = response.json()
    assert "type" in data
    assert "features" in data
    assert "FeatureCollection" == data["type"]
    assert len(expected_response) == len(data["features"])
    assert expected_response == data["features"]


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


def test_old_entity_redirects_as_expected(
    test_data_old_entities, client, exclude_middleware
):
    """
    Test entity endpoint returns a 302 response code when old_entity requested
    """
    old_entity = test_data_old_entities["old_entities"][301][0]
    response = client.get(f"/entity/{old_entity.old_entity_id}", allow_redirects=False)
    assert response.status_code == 301
    assert response.headers["location"] == f"/entity/{old_entity.new_entity_id}"


def test_old_entity_redirects_as_expected_with_suffix(
    test_data_old_entities, client, exclude_middleware
):
    """
    Test entity endpoint returns a 302 response code when old_entity requested
    """
    old_entity = test_data_old_entities["old_entities"][301][0]
    response = client.get(
        f"/entity/{old_entity.old_entity_id}.json", allow_redirects=False
    )
    assert response.status_code == 301
    assert response.headers["location"] == f"/entity/{old_entity.new_entity_id}.json"


def test_old_entity_gone_shown(test_data_old_entities, client, exclude_middleware):
    """
    Test entity endpoint returns entity gone content
    """
    old_entity = test_data_old_entities["old_entities"][410][0]
    response = client.get(f"/entity/{old_entity.old_entity_id}", allow_redirects=False)
    assert response.status_code == 200
    assert (
        f"This entity (#{old_entity.old_entity_id}) has been removed." in response.text
    )


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


def test_link_dataset_endpoint_returns_as_expected(
    test_data, test_settings, client, exclude_middleware
):
    """
    Test link dataset endpoint returns a 302 response code with the S3_HOISTED_BUCKET domain
    """
    response = client.get("/dataset/greenspace.csv/link", allow_redirects=False)
    assert response.status_code == 302
    assert (
        response.headers["location"]
        == f"{test_settings.S3_HOISTED_BUCKET}/greenspace-hoisted.csv"
    )
