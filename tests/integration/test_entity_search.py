import pytest

from application.core.models import EntityModel
from application.data_access.entity_queries import get_entity_search
from application.search.enum import EntriesOption, GeometryRelation


@pytest.fixture(scope="module")
def raw_params():
    return {
        "theme": None,
        "typology": None,
        "dataset": None,
        "organisation": None,
        "organisation_entity": None,
        "entity": None,
        "curie": None,
        "prefix": None,
        "reference": None,
        "related_entity": None,
        "entries": EntriesOption.all,
        "start_date": None,
        "start_date_year": None,
        "start_date_month": None,
        "start_date_day": None,
        "start_date_match": None,
        "end_date": None,
        "end_date_year": None,
        "end_date_month": None,
        "end_date_day": None,
        "end_date_match": None,
        "entry_date": None,
        "entry_date_year": "",
        "entry_date_month": "",
        "entry_date_day": "",
        "entry_date_match": None,
        "longitude": None,
        "latitude": None,
        "geometry": None,
        "geometry_entity": None,
        "geometry_reference": None,
        "geometry_relation": None,
        "limit": 10,
        "offset": None,
        "suffix": None,
        "field": None,
    }


@pytest.fixture()
def params(raw_params):
    return raw_params.copy()


def test_search_entity_by_dataset_name_not_in_system(test_data, params):

    params["dataset"] = ["not-exists"]
    result = get_entity_search(params)
    assert result["count"] == 0
    assert result["entities"] == []


def test_search_entity_by_dataset_name_not_in_system_returns_error(
    test_data, client, exclude_middleware
):
    response = client.get("/entity.json?dataset=not-exists")
    assert response.status_code == 400
    assert response.json() == {
        "detail": [
            {
                "ctx": {
                    "dataset_names": [
                        "greenspace",
                        "forest",
                        "brownfield-site",
                        "historical-monument",
                    ]
                },
                "loc": ["dataset"],
                "msg": "Requested datasets do not exist: not-exists. Valid "
                "dataset names: "
                "greenspace,forest,brownfield-site,historical-monument",
                "type": "value_error.datasetvaluenotfound",
            }
        ]
    }


def test_search_entity_by_dataset_names_not_in_system_returns_only_missing(
    test_data, client, exclude_middleware
):
    response = client.get("/entity.json?dataset=not-exists&dataset=greenspace")
    assert response.status_code == 400

    assert response.json() == {
        "detail": [
            {
                "ctx": {
                    "dataset_names": [
                        "greenspace",
                        "forest",
                        "brownfield-site",
                        "historical-monument",
                    ]
                },
                "loc": ["dataset"],
                "msg": "Requested datasets do not exist: not-exists. Valid "
                "dataset names: "
                "greenspace,forest,brownfield-site,historical-monument",
                "type": "value_error.datasetvaluenotfound",
            }
        ]
    }


def test_search_entity_by_single_dataset_name(test_data, params):

    params["dataset"] = ["greenspace"]
    result = get_entity_search(params)
    assert 1 == result["count"]
    entity = result["entities"][0]
    assert entity.dataset == "greenspace"
    assert entity.typology == "geography"


def test_search_entity_by_list_of_dataset_names(test_data, params):

    params["dataset"] = ["greenspace", "brownfield-site"]
    result = get_entity_search(params)
    assert 2 == result["count"]
    for e in result["entities"]:
        assert e.dataset in ["greenspace", "brownfield-site"]
        assert e.typology == "geography"


def test_search_entity_by_date_since(test_data, params):

    params["entry_date_year"] = 2019
    params["entry_date_month"] = 1
    params["entry_date_day"] = 1
    params["entry_date_match"] = "since"

    result = get_entity_search(params)
    assert 4 == result["count"]
    for e in result["entities"]:
        assert e.dataset in [
            "greenspace",
            "forest",
            "brownfield-site",
            "historical-monument",
        ]
        assert "geography" == e.typology

    params["entry_date_year"] = 2020
    result = get_entity_search(params)
    assert 3 == result["count"]
    for e in result["entities"]:
        assert e.dataset in ["forest", "brownfield-site", "historical-monument"]
        assert e.dataset != "greenspace"

    params["entry_date_year"] = 2021
    result = get_entity_search(params)
    assert 2 == result["count"]
    for e in result["entities"]:
        assert e.dataset in ["brownfield-site", "historical-monument"]
        assert e.dataset not in ["greenspace", "forest"]

    params["entry_date_year"] = 2022
    result = get_entity_search(params)
    assert 1 == result["count"]
    for e in result["entities"]:
        assert e.dataset in ["historical-monument"]
        assert e.dataset not in ["greenspace", "forest", "brownfield-site"]

    params["entry_date_year"] = 2023
    result = get_entity_search(params)
    assert result["count"] == 0


def test_search_entity_by_date_before(test_data, params):

    params["entry_date_year"] = 2019
    params["entry_date_month"] = 1
    params["entry_date_day"] = 1
    params["entry_date_match"] = "before"

    result = get_entity_search(params)
    assert 0 == result["count"]

    params["entry_date_year"] = 2020
    result = get_entity_search(params)
    assert 1 == result["count"]

    params["entry_date_year"] = 2021
    result = get_entity_search(params)
    assert 2 == result["count"]

    params["entry_date_year"] = 2022
    result = get_entity_search(params)
    assert 3 == result["count"]

    params["entry_date_year"] = 2023
    result = get_entity_search(params)
    assert 4 == result["count"]
    for e in result["entities"]:
        assert e.dataset in [
            "greenspace",
            "forest",
            "brownfield-site",
            "historical-monument",
        ]


def test_search_entity_by_date_equal(test_data, params):

    params["entry_date_year"] = 2019
    params["entry_date_month"] = 1
    params["entry_date_day"] = 1

    result = get_entity_search(params)
    assert 0 == result["count"]

    params["entry_date_day"] = 7

    result = get_entity_search(params)
    assert 1 == result["count"]
    entity = result["entities"][0]
    assert entity.dataset == "greenspace"


def test_search_entity_by_point(test_data, params):

    params["longitude"] = -1.64794921875
    params["latitude"] = 50.51342652633956

    result = get_entity_search(params)
    assert 0 == result["count"]

    params["longitude"] = -1.82398796081543
    params["latitude"] = 51.18064775509972

    result = get_entity_search(params)
    assert 1 == result["count"]
    entity = result["entities"][0]
    assert entity.dataset == "historical-monument"


def test_search_entity_by_single_polygon_intersects(test_data, params):

    from tests.test_data.wkt_data import intersects_with_brownfield_entity as brownfield
    from tests.test_data.wkt_data import intersects_with_greenspace_entity as greenspace

    params["geometry"] = [brownfield]
    params["geometry_relation"] = GeometryRelation.intersects.name

    result = get_entity_search(params)
    assert 1 == result["count"]
    entity = result["entities"][0]
    assert "brownfield-site" == entity.dataset

    params["geometry"] = [greenspace]
    result = get_entity_search(params)
    assert 1 == result["count"]
    entity = result["entities"][0]
    assert entity.dataset == "greenspace"


def test_search_entity_by_list_of_polygons_that_intersect(test_data, params):

    from tests.test_data.wkt_data import intersects_with_brownfield_entity as brownfield
    from tests.test_data.wkt_data import intersects_with_greenspace_entity as greenspace

    params["geometry"] = [brownfield, greenspace]
    params["geometry_relation"] = GeometryRelation.intersects.name

    result = get_entity_search(params)
    assert result["count"] == 2


def test_search_entity_by_polygon_with_no_intersection(test_data, params):

    from tests.test_data.wkt_data import no_intersection

    params["geometry"] = [no_intersection]
    params["geometry_relation"] = GeometryRelation.intersects.name

    result = get_entity_search(params)
    assert 0 == result["count"]


def test_search_all_entities(test_data, params):

    # default is EntriesOption.all - already in params
    result = get_entity_search(params)
    assert 4 == result["count"]
    for e in result["entities"]:
        assert e.dataset in [
            "greenspace",
            "forest",
            "brownfield-site",
            "historical-monument",
        ]


def test_search_current_entries(test_data, params):

    # entries without an end date
    params["entries"] = EntriesOption.current

    result = get_entity_search(params)
    assert 3 == result["count"]
    for e in result["entities"]:
        assert e.dataset in [
            "forest",
            "brownfield-site",
            "historical-monument",
        ]


def test_search_historical_entries(test_data, params):

    # entries with an end date
    params["entries"] = EntriesOption.historical

    result = get_entity_search(params)
    assert 1 == result["count"]
    e = result["entities"][0]
    assert e.dataset == "greenspace"


def test_search_includes_only_field_params(test_data, client, exclude_middleware):
    response = client.get("/entity.json?limit=10&field=name")
    response.raise_for_status()
    result = response.json()
    assert result["count"] == 4
    e = result["entities"][0]
    assert not set(e.keys()).symmetric_difference(set(["name"]))


def test_search_includes_multiple_field_params(test_data, client, exclude_middleware):
    response = client.get("/entity.json?limit=10&field=name&field=dataset")
    response.raise_for_status()
    result = response.json()
    assert result["count"] == 4
    e = result["entities"][0]
    assert not set(e.keys()).symmetric_difference(set(["name", "dataset"]))


@pytest.mark.parametrize("field_name", list(EntityModel.schema()["properties"].keys()))
def test_search_includes_any_field_params(
    field_name, test_data, client, exclude_middleware
):
    response = client.get(f"/entity.json?limit=10&field={field_name}")
    response.raise_for_status()
    result = response.json()
    assert result["count"] == 4
    e = result["entities"][0]
    assert not set(e.keys()).symmetric_difference(set([field_name]))


def test_search_pagination_does_not_affect_count(test_data, client, exclude_middleware):
    response = client.get("/entity.json?limit=1")
    response.raise_for_status()
    result = response.json()
    assert result["count"] == 4


def test_search_filtering_does_affect_count(test_data, client, exclude_middleware):
    response = client.get("/entity.json?limit=1&dataset=greenspace")
    response.raise_for_status()
    result = response.json()
    assert result["count"] == 1


def test_search_disjoint_geometry_should_return_all_data(test_data, params):

    from tests.test_data.wkt_data import no_intersection

    params["geometry"] = [no_intersection]
    params["geometry_relation"] = GeometryRelation.disjoint.name

    result = get_entity_search(params)
    assert 4 == result["count"]


def test_search_by_geometry_that_is_contained_by_another_should_return_containing_entity(
    test_data, params
):

    from tests.test_data.wkt_data import contained_by_greenspace_entity

    params["geometry"] = [contained_by_greenspace_entity]
    params["geometry_relation"] = GeometryRelation.contains.name

    result = get_entity_search(params)
    assert 1 == result["count"]
    assert result["entities"][0].dataset == "greenspace"


def test_search_by_geometry_that_equals_that_of_an_entity_should_return_the_entity(
    test_data, params
):

    from tests.test_data.wkt_data import equals_brownfield_site_entity

    params["geometry"] = [equals_brownfield_site_entity]
    params["geometry_relation"] = GeometryRelation.equals.name

    result = get_entity_search(params)
    assert 1 == result["count"]
    assert result["entities"][0].dataset == "brownfield-site"
