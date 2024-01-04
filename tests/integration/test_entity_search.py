import pytest
import logging
from application.core.models import EntityModel
from application.data_access.entity_queries import get_entity_search
from application.search.enum import PeriodOption, GeometryRelation


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
        "entries": PeriodOption.all,
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


def test_search_entity_by_dataset_name_not_in_system_returns_error(
    test_data, client, exclude_middleware
):
    response = client.get("/entity.json?dataset=not-exists")
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "ctx": {
                    "dataset_names": [
                        "greenspace",
                        "forest",
                        "brownfield-site",
                        "historical-monument",
                        "tree",
                        "conservation-area",
                    ]
                },
                "loc": ["dataset"],
                "msg": "Requested datasets do not exist: not-exists. Valid "
                "dataset names: "
                "greenspace,forest,brownfield-site,historical-monument,tree,conservation-area",
                "type": "value_error.datasetvaluenotfound",
            }
        ]
    }


def test_search_entity_by_dataset_names_not_in_system_returns_only_missing(
    test_data, client, exclude_middleware
):
    response = client.get("/entity.json?dataset=not-exists&dataset=greenspace")
    assert response.status_code == 422
    logging.warning(response.json())
    assert response.json() == {
        "detail": [
            {
                "ctx": {
                    "dataset_names": [
                        "greenspace",
                        "forest",
                        "brownfield-site",
                        "historical-monument",
                        "tree",
                        "conservation-area",
                    ]
                },
                "loc": ["dataset"],
                "msg": "Requested datasets do not exist: not-exists. Valid "
                "dataset names: "
                "greenspace,forest,brownfield-site,historical-monument,tree,conservation-area",
                "type": "value_error.datasetvaluenotfound",
            }
        ]
    }


def test_search_entity_by_single_dataset_name(test_data, params, mocker, db_session):
    params["dataset"] = ["greenspace"]
    result = get_entity_search(db_session, params)
    assert 1 == result["count"]
    entity = result["entities"][0]
    assert entity.dataset == "greenspace"
    assert entity.typology == "geography"


def test_search_entity_by_list_of_dataset_names(test_data, params, db_session):
    params["dataset"] = ["greenspace", "brownfield-site"]
    result = get_entity_search(db_session, params)
    assert 2 == result["count"]
    for e in result["entities"]:
        assert e.dataset in ["greenspace", "brownfield-site", "conservation-area"]
        assert e.typology == "geography"


def test_search_entity_by_date_since(test_data, params, db_session):
    params["entry_date_year"] = 2019
    params["entry_date_month"] = 1
    params["entry_date_day"] = 1
    params["entry_date_match"] = "since"
    result = get_entity_search(db_session, params)
    assert result["count"] == len(test_data["entities"])
    for e in result["entities"]:
        assert e.dataset in [
            "greenspace",
            "forest",
            "brownfield-site",
            "historical-monument",
            "tree",
            "conservation-area",
            "local-authority",
        ]

    params["entry_date_year"] = 2020
    result = get_entity_search(db_session, params)
    assert result["count"] == len(test_data["entities"]) - 1
    for e in result["entities"]:
        assert e.dataset in [
            "forest",
            "brownfield-site",
            "historical-monument",
            "conservation-area",
            "tree",
            "local-authority",
        ]
        assert e.dataset != "greenspace"

    params["entry_date_year"] = 2021
    result = get_entity_search(db_session, params)
    assert result["count"] == len(test_data["entities"]) - 3
    for e in result["entities"]:
        assert e.dataset in [
            "brownfield-site",
            "historical-monument",
            "tree",
            "local-authority",
            "conservation-area",
        ]
        assert e.dataset not in ["greenspace", "forest"]

    params["entry_date_year"] = 2022
    result = get_entity_search(db_session, params)
    assert result["count"] == len(test_data["entities"]) - 7
    for e in result["entities"]:
        assert e.dataset in [
            "historical-monument",
            "local-authority",
            "conservation-area",
        ]
        assert e.dataset not in [
            "greenspace",
            "forest",
            "brownfield-site",
            "tree",
        ]

    params["entry_date_year"] = 2023
    result = get_entity_search(db_session, params)
    assert result["count"] == 0


def test_search_entity_by_date_before(test_data, params, db_session):
    params["entry_date_year"] = 2019
    params["entry_date_month"] = 1
    params["entry_date_day"] = 1
    params["entry_date_match"] = "before"

    result = get_entity_search(db_session, params)
    assert 0 == result["count"]

    params["entry_date_year"] = 2020
    result = get_entity_search(db_session, params)
    assert 1 == result["count"]

    params["entry_date_year"] = 2021
    result = get_entity_search(db_session, params)
    assert 3 == result["count"]

    params["entry_date_year"] = 2022
    result = get_entity_search(db_session, params)
    assert 7 == result["count"]

    params["entry_date_year"] = 2023
    result = get_entity_search(db_session, params)
    assert result["count"] == len(test_data["entities"])
    for e in result["entities"]:
        assert e.dataset in [
            "greenspace",
            "forest",
            "brownfield-site",
            "historical-monument",
            "conservation-area",
            "tree",
            "local-authority",
        ]


def test_search_entity_by_date_equal(test_data, params, db_session):
    params["entry_date_year"] = 2019
    params["entry_date_month"] = 1
    params["entry_date_day"] = 1

    result = get_entity_search(db_session, params)
    assert 0 == result["count"]

    params["entry_date_day"] = 7

    result = get_entity_search(db_session, params)
    assert 1 == result["count"]
    entity = result["entities"][0]
    assert entity.dataset == "greenspace"


def test_search_entity_by_point(test_data, params, db_session):
    params["longitude"] = -1.64794921875
    params["latitude"] = 50.51342652633956

    result = get_entity_search(db_session, params)
    assert 0 == result["count"]

    params["longitude"] = -1.82398796081543
    params["latitude"] = 51.18064775509972

    result = get_entity_search(db_session, params)
    assert 1 == result["count"]
    entity = result["entities"][0]
    assert entity.dataset == "historical-monument"


def test_search_entity_by_single_polygon_intersects(test_data, params, db_session):
    from tests.test_data.wkt_data import intersects_with_brownfield_entity as brownfield
    from tests.test_data.wkt_data import intersects_with_greenspace_entity as greenspace

    params["geometry"] = [brownfield]
    params["geometry_relation"] = GeometryRelation.intersects.name

    result = get_entity_search(db_session, params)
    assert 1 == result["count"]
    entity = result["entities"][0]
    assert "brownfield-site" == entity.dataset

    params["geometry"] = [greenspace]
    result = get_entity_search(db_session, params)
    assert 1 == result["count"]
    entity = result["entities"][0]
    assert entity.dataset == "greenspace"


def test_search_entity_by_list_of_polygons_that_intersect(
    test_data, params, db_session
):
    from tests.test_data.wkt_data import intersects_with_brownfield_entity as brownfield
    from tests.test_data.wkt_data import intersects_with_greenspace_entity as greenspace

    params["geometry"] = [brownfield, greenspace]
    params["geometry_relation"] = GeometryRelation.intersects.name

    result = get_entity_search(db_session, params)
    assert result["count"] == 2


def test_search_entity_by_polygon_with_no_intersection(test_data, params, db_session):
    from tests.test_data.wkt_data import no_intersection

    params["geometry"] = [no_intersection]
    params["geometry_relation"] = GeometryRelation.intersects.name

    result = get_entity_search(db_session, params)
    assert 0 == result["count"]


def test_search_all_entities(test_data, params, db_session):
    # default is PeriodOption.all - already in params
    result = get_entity_search(db_session, params)
    assert result["count"] == len(test_data["entities"])
    for e in result["entities"]:
        assert e.dataset in [
            "greenspace",
            "forest",
            "brownfield-site",
            "historical-monument",
            "tree",
            "conservation-area",
            "local-authority",
        ]


def test_search_current_entries(test_data, params, db_session):
    # entries without an end date
    params["period"] = [PeriodOption.current]

    result = get_entity_search(db_session, params)
    assert result["count"] == 10
    for e in result["entities"]:
        assert e.dataset in [
            "forest",
            "brownfield-site",
            "historical-monument",
            "tree",
            "conservation-area",
            "local-authority",
        ]


def test_search_historical_entries(test_data, params, db_session):
    # entries with an end date
    params["period"] = [PeriodOption.historical]

    result = get_entity_search(db_session, params)
    assert 1 == result["count"]
    e = result["entities"][0]
    assert e.dataset == "greenspace"


def test_search_includes_only_field_params(test_data, client, exclude_middleware):
    response = client.get("/entity.json?limit=10&field=name")
    response.raise_for_status()
    result = response.json()
    assert result["count"] == len(test_data["entities"])
    e = result["entities"][0]
    assert not set(e.keys()).symmetric_difference(set(["name", "entity"]))


def test_search_includes_multiple_field_params(test_data, client, exclude_middleware):
    response = client.get("/entity.json?limit=10&field=name&field=dataset")
    response.raise_for_status()
    result = response.json()
    assert result["count"] == len(test_data["entities"])
    e = result["entities"][0]
    assert not set(e.keys()).symmetric_difference(set(["name", "dataset", "entity"]))


# geojson needs to be removed from model
@pytest.mark.parametrize(
    "field_name", list(EntityModel.schema()["properties"].keys() - {"geojson"})
)
def test_search_includes_any_field_params(
    field_name, test_data, client, exclude_middleware
):
    response = client.get(f"/entity.json?limit=10&field={field_name}")
    response.raise_for_status()
    result = response.json()
    assert result["count"] == len(test_data["entities"])
    e = result["entities"][0]
    assert not set(e.keys()).symmetric_difference(set([field_name, "entity"]))


def test_search_pagination_does_not_affect_count(test_data, client, exclude_middleware):
    response = client.get("/entity.json?limit=1")
    response.raise_for_status()
    result = response.json()
    assert result["count"] == len(test_data["entities"])


def test_search_filtering_does_affect_count(test_data, client, exclude_middleware):
    response = client.get("/entity.json?limit=1&dataset=greenspace")
    response.raise_for_status()
    result = response.json()
    assert result["count"] == 1


def test_search_entity_equal_to_a_polygon(test_data, params, db_session):
    from tests.test_data.wkt_data import equals_brownfield_site_entity

    params["geometry"] = [equals_brownfield_site_entity]
    params["geometry_relation"] = GeometryRelation.equals.name

    result = get_entity_search(db_session, params)
    assert result["count"] == 1
    assert result["entities"][0].dataset == "brownfield-site"


def test_search_entity_disjoint_from_a_polygon(test_data, params, db_session):
    from tests.test_data.wkt_data import no_intersection

    params["geometry"] = [no_intersection]
    params["geometry_relation"] = GeometryRelation.disjoint.name

    result = get_entity_search(db_session, params)
    assert result["count"] == 9


def test_search_entity_that_polygon_touches(test_data, params, mocker, db_session):
    from tests.test_data.wkt_data import touches_forest_entity

    params["geometry"] = [touches_forest_entity]
    params["geometry_relation"] = GeometryRelation.touches.name

    result = get_entity_search(db_session, params)
    assert result["count"] == 1
    assert result["entities"][0].dataset == "forest"


def test_search_entity_that_contains_a_polygon(test_data, params, db_session):
    from tests.test_data.wkt_data import contained_by_greenspace_entity

    params["geometry"] = [contained_by_greenspace_entity]
    params["geometry_relation"] = GeometryRelation.contains.name

    result = get_entity_search(db_session, params)
    assert result["count"] == 1
    assert result["entities"][0].dataset == "greenspace"


# when dealing with polygons contains and covers are synonymous
def test_search_entity_that_covers_a_polygon(test_data, params, db_session):
    from tests.test_data.wkt_data import contained_by_greenspace_entity

    params["geometry"] = [contained_by_greenspace_entity]
    params["geometry_relation"] = GeometryRelation.covers.name

    result = get_entity_search(db_session, params)
    assert result["count"] == 1
    assert result["entities"][0].dataset == "greenspace"


def test_search_entity_covered_by_a_polygon(test_data, params, db_session):
    from tests.test_data.wkt_data import covers_historical_monument_entity

    params["geometry"] = [covers_historical_monument_entity]
    params["geometry_relation"] = GeometryRelation.coveredby.name

    result = get_entity_search(db_session, params)
    assert result["count"] == 1
    assert result["entities"][0].dataset == "historical-monument"


def test_search_entity_that_overlaps_a_polygon(test_data, params, db_session):
    from tests.test_data.wkt_data import intersects_with_brownfield_entity

    params["geometry"] = [intersects_with_brownfield_entity]
    params["geometry_relation"] = GeometryRelation.overlaps.name

    result = get_entity_search(db_session, params)
    assert result["count"] == 1
    assert result["entities"][0].dataset == "brownfield-site"


def test_search_entity_that_is_crossed_by_a_line(test_data, params, db_session):
    from tests.test_data.wkt_data import crosses_historical_entity

    params["geometry"] = [crosses_historical_entity]
    params["geometry_relation"] = GeometryRelation.crosses.name

    result = get_entity_search(db_session, params)
    assert result["count"] == 1
    assert result["entities"][0].dataset == "historical-monument"


def test_search_geometry_entity_returns_entities_that_intersect_with_entity(
    test_data, params, db_session
):
    test_conservation_area = [
        e for e in test_data["entities"] if e["dataset"] == "conservation-area"
    ][0]
    test_trees = set(
        [int(e["entity"]) for e in test_data["entities"] if e["dataset"] == "tree"]
    )

    params["geometry_entity"] = [test_conservation_area.get("entity")]
    params["dataset"] = ["tree"]
    result = get_entity_search(db_session, params)
    assert result["count"] == 3
    for e in result["entities"]:
        assert e.dataset == "tree"
        assert e.entity in test_trees


def test_search_entity_by_curie(test_data, params, db_session):

    expected_entity = [
        e
        for e in test_data["entities"]
        if e["prefix"] == "greenspace" and e["reference"] == "Q1234567"
    ][0]

    curie = f"{expected_entity['prefix']}:{expected_entity['reference']}"
    params["curie"] = [curie]

    result = get_entity_search(db_session, params)

    assert result["count"] == 1

    entity = result["entities"][0]

    assert entity.prefix == expected_entity["prefix"]
    assert entity.reference == expected_entity["reference"]


def test_search_entity_by_organisation_curie(test_data, params, db_session):

    expected_entity = [
        e
        for e in test_data["entities"]
        if e["prefix"] == "local-authority" and e["reference"] == "DAC"
    ][0]

    curie = f"{expected_entity['prefix']}:{expected_entity['reference']}"
    params["curie"] = [curie]

    result = get_entity_search(db_session, params)

    assert result["count"] == 1

    entity = result["entities"][0]

    assert entity.prefix == expected_entity["prefix"]
    assert entity.reference == expected_entity["reference"]


# TODO test cases for contains, within
