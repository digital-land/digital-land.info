from copy import deepcopy

import pytest as pytest

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
    dataset["github-discussion"] = dataset.pop("github_discussion") or ""
    dataset["entity-minimum"] = dataset.pop("entity_minimum") or ""
    dataset["entity-maximum"] = dataset.pop("entity_maximum") or ""
    dataset["phase"] = dataset.pop("phase") or ""
    dataset["replacement-dataset"] = dataset.pop("replacement_dataset") or ""
    dataset["version"] = dataset.pop("version") or ""
    dataset["realm"] = dataset.pop("realm") or ""

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
    response = client.get("/entity.geojson", headers={"Origin": "localhost"})
    data = response.json()
    assert "type" in data
    assert "features" in data
    assert "FeatureCollection" == data["type"]
    assert len(
        [
            e
            for e in test_data["entities"][
                :10
            ]  # only first 10 entities as we limit in the query
            if e.get("geometry", None) is not None or e.get("point", None) is not None
        ]
    ) == len(data["features"])


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


def test_old_entity_redirects_as_expected(test_data_old_entities, client):
    """
    Test entity endpoint returns a 302 response code when old_entity requested
    """
    old_entity = test_data_old_entities["old_entities"][301][0]
    response = client.get(f"/entity/{old_entity.old_entity_id}", allow_redirects=False)
    assert response.status_code == 301
    assert response.headers["location"] == f"/entity/{old_entity.new_entity_id}"


def test_old_entity_redirects_as_expected_with_suffix(test_data_old_entities, client):
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
    assert response.status_code == 410
    assert (
        f"This entity (#{old_entity.old_entity_id}) has been removed." in response.text
    )
    assert (
        "text/html" in response.headers["Content-Type"]
    ), "Expected response in text/html format"


def test_old_entity_gone_json_shown(test_data_old_entities, client, exclude_middleware):
    """
    Test entity endpoint returns entity gone content
    """
    old_entity = test_data_old_entities["old_entities"][410][0]
    response = client.get(
        f"/entity/{old_entity.old_entity_id}.json", allow_redirects=False
    )
    assert response.status_code == 410
    assert (
        response.headers["Content-Type"] == "application/json"
    ), "Expected response in JSON format"
    assert f"Entity {old_entity.old_entity_id} has been removed" in response.text


def test_dataset_json_endpoint_returns_as_expected(test_data, client):
    datasets = test_data["datasets"]
    response = client.get("/dataset.json")
    assert response.status_code == 200
    data = response.json()
    assert "datasets" in data
    assert len(data["datasets"]) > 0
    # TODO find way of generating these field values from fixtures
    for dataset in data["datasets"]:
        assert dataset.pop("themes")
        assert dataset.pop("entity-count")
        assert "entities" in dataset
        dataset.pop("entities")
        attribution_txt = dataset.pop("attribution-text")
        assert attribution_txt == "attribution text"
        licence_txt = dataset.pop("licence-text")
        assert licence_txt == "licence text"

    assert sorted(data["datasets"], key=lambda x: x["name"]) == sorted(
        _transform_dataset_fixture_to_response(deepcopy(datasets)),
        key=lambda x: x["name"],
    )


wkt_params = [
    ("POINT (-0.33753991127014155 53.74458682618967)", 200),
    ("'POINT (-0.33753991127014155 53.74458682618967)'", 422),
    ('"POINT (-0.33753991127014155 53.74458682618967)"', 422),
    ("POINT (-0.33753991127014155)", 422),
    ("POLYGON ((-0.33753991127014155)", 422),
    ("MULTIPOLYGON ((-0.33753991127014155)))", 422),
    ("\t", 422),
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
        ["query", "entry_date_year"],
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
        ["query", "start_date_year"],
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
        ["query", "end_date_year"],
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
    assert response.status_code == 422
    data = response.json()
    assert expected == data["detail"][0]["loc"]


curie_params = ["", ":", "broken", "bro-ken", "bro;ken", "bro\tken"]


@pytest.mark.parametrize("curie", curie_params)
def test_search_entity_rejects_invalid_curie(curie, client):
    params = {"curie": curie}
    response = client.get("/entity.json", params=params)
    assert response.status_code == 422
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
    expected_content = "Page not found"
    # Check if the expected content is present in the response body
    assert expected_content in response.text


def test_get_dataset_unknown_returns_404(client, exclude_middleware):
    response = client.get("/dataset/waste-authority")
    assert response.status_code == 404


def test_get_dataset_as_json_returns_json(client, exclude_middleware, test_data):
    response = client.get("/dataset/greenspace.json")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"


def test_dataset_json_has_licence_and_attribution(
    client, exclude_middleware, test_data
):
    response = client.get("/dataset/greenspace.json")
    assert response.status_code == 200
    data = response.json()
    assert data["dataset"] == "greenspace"
    assert data["attribution"] == "crown-copyright"
    assert data["licence"] == "ogl3"
