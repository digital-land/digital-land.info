from copy import deepcopy

import pytest as pytest

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


wkt_params = [
    ("POINT (-0.33753991127014155 53.74458682618967)", 200),
    ("'POINT (-0.33753991127014155 53.74458682618967)'", 400),
    ('"POINT (-0.33753991127014155 53.74458682618967)"', 400),
    ("POINT (-0.33753991127014155)", 400),
    ("POLYGON ((-0.33753991127014155)", 400),
    ("MULTIPOLYGON ((-0.33753991127014155)))", 400),
    ("\t", 400),
]


@pytest.mark.parametrize("point, expected_status_code", wkt_params)
def test_api_handles_invalid_wkt(point, expected_status_code, client, test_data):

    params = {"geometry_relation": "intersects", "geometry": point}
    response = client.get("/entity.geojson", params=params)
    assert response.status_code == expected_status_code
    data = response.json()
    if data.get("detail") is not None:
        assert f"Invalid geometry {point}" == data["detail"][0]["msg"]


def test_search_by_entity_and_geometry_entity_require_numeric_id(client, test_data):
    params = {"geometry_entity": "not a number"}
    response = client.get("/entity.geojson", params=params)
    assert response.status_code == 422
    data = response.json()
    assert "value is not a valid integer" == data["detail"][0]["msg"]
    assert "geometry_entity" == data["detail"][0]["loc"][1]

    params = {"entity": "not a number"}
    response = client.get("/entity.geojson", params=params)
    assert response.status_code == 422
    data = response.json()
    assert "value is not a valid integer" == data["detail"][0]["msg"]
    assert "entity" == data["detail"][0]["loc"][1]


date_params = [
    (
        ["entry_date_day"],
        {"entry_date_year": 2022, "entry_date_month": 11, "entry_date_day": -1},
    ),
    (
        ["entry_date_day"],
        {"entry_date_year": 2022, "entry_date_month": 11, "entry_date_day": 32},
    ),
    (
        ["entry_date_month"],
        {"entry_date_year": 2022, "entry_date_month": -1, "entry_date_day": 1},
    ),
    (
        ["entry_date_month"],
        {"entry_date_year": 2022, "entry_date_month": 13, "entry_date_day": 1},
    ),
    (
        ["entry_date_year"],
        {
            "entry_date_year": "twenty_twenty_two",
            "entry_date_month": 1,
            "entry_date_day": 1,
        },
    ),
    (
        ["start_date_day"],
        {"star_date_year": 2022, "start_date_month": 11, "start_date_day": -1},
    ),
    (
        ["start_date_day"],
        {"start_date_year": 2022, "start_date_month": 11, "start_date_day": 32},
    ),
    (
        ["start_date_month"],
        {"start_date_year": 2022, "start_date_month": -1, "start_date_day": 1},
    ),
    (
        ["start_date_month"],
        {"start_date_year": 2022, "start_date_month": 13, "start_date_day": 1},
    ),
    (
        ["start_date_year"],
        {
            "start_date_year": "twenty_twenty_two",
            "start_date_month": 1,
            "start_date_day": 1,
        },
    ),
    (
        ["end_date_day"],
        {"end_date_year": 2022, "end_date_month": 11, "end_date_day": -1},
    ),
    (
        ["end_date_day"],
        {"end_date_year": 2022, "end_date_month": 11, "end_date_day": 32},
    ),
    (
        ["end_date_month"],
        {"end_date_year": 2022, "end_date_month": -1, "end_date_day": 1},
    ),
    (
        ["end_date_month"],
        {"end_date_year": 2022, "end_date_month": 13, "end_date_day": 1},
    ),
    (
        ["end_date_year"],
        {"end_date_year": "twenty_twenty_two", "end_date_month": 1, "end_date_day": 1},
    ),
    (
        ["end_date_month"],
        {"end_date_year": 2022, "end_date_month": "-1", "end_date_day": 1},
    ),
    (
        ["end_date_day"],
        {"end_date_year": 2022, "end_date_month": 1, "end_date_day": "33"},
    ),
]


@pytest.mark.parametrize("expected, params", date_params)
def test_api_requires_numeric_date_fields_in_range(expected, params, client):
    response = client.get("/entity.geojson", params=params)
    assert response.status_code == 400
    data = response.json()
    assert expected == data["detail"][0]["loc"]


curie_params = ["", ":", "broken", "bro-ken", "bro;ken", "bro\tken"]


@pytest.mark.parametrize("curie", curie_params)
def test_search_entity_rejects_invalid_curie(curie, client):
    params = {"curie": curie}
    response = client.get("/entity.json", params=params)
    assert response.status_code == 400
    data = response.json()
    assert "curie must be in form 'prefix:reference'" == data["detail"][0]["msg"]
    assert "curie" == data["detail"][0]["loc"][0]


def test_get_by_curie_redirects_to_entity(test_data, client, exclude_middleware):
    greenspace = test_data["entities"][0]
    prefix = greenspace["prefix"]
    reference = greenspace["reference"]
    entity = greenspace["entity"]

    response = client.get(f"/curie/{prefix}:{reference}", allow_redirects=False)
    assert response.status_code == 303
    assert f"http://testserver/entity/{entity}" == response.headers["location"]

    response = client.get(
        f"/prefix/{prefix}/reference/{reference}", allow_redirects=False
    )
    assert response.status_code == 303
    assert f"http://testserver/entity/{entity}" == response.headers["location"]


def test_get_by_curie_404s_for_unknown_reference(test_data, client, exclude_middleware):
    response = client.get("/curie/not:found", allow_redirects=False)
    assert response.status_code == 404


def test_get_dataset_unknown_returns_404(client, exclude_middleware):
    response = client.get("/dataset/waste-authority")
    assert response.status_code == 404


def test_get_dataset_as_json_returns_json(client, exclude_middleware):
    response = client.get("/dataset/greenspace.json")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
