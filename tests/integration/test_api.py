from tests.test_data.wkt_data import somewhere_in_lambeth, somewhere_in_normandy

# These test actually run against live data. When moved to postgres we should use
# test data as part of this repo to flesh out test cases. At the moment no detailed
# assertions made on details of data results as they are real and can change.


def test_app_returns_valid_geojson_list(client):

    response = client.get(
        "/entity.geojson?dataset=not-real", headers={"Origin": "localhost"}
    )
    data = response.json()
    assert "type" in data
    assert "features" in data
    assert "FeatureCollection" == data["type"]
    assert [] == data["features"]


def test_lasso_geo_search_finds_results(client):
    params = {"geometry_relation": "intersects", "geometry": somewhere_in_lambeth}
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


def test_lasso_geo_search_finds_no_results(client):
    params = {"geometry_relation": "intersects", "geometry": somewhere_in_normandy}
    response = client.get("/entity.geojson", params=params)
    assert response.status_code == 200
    data = response.json()
    assert "type" in data
    assert "features" in data
    assert "FeatureCollection" == data["type"]
    assert [] == data["features"]
