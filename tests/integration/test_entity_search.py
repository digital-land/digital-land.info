from application.data_access.entity_queries import get_entity_search
from application.search.enum import EntriesOption

raw_params = {
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
}


def test_search_entity_by_dataset_name(test_data):
    params = raw_params.copy()
    params["dataset"] = ["not-exists"]
    result = get_entity_search(params)
    assert 0 == result["count_all"]
    assert [] == result["entities"]

    params["dataset"] = ["greenspace"]
    result = get_entity_search(params)
    assert 1 == result["count_all"]
    entity = result["entities"][0]
    assert "greenspace" == entity.dataset
    assert "geography" == entity.typology

    params["dataset"] = ["greenspace", "brownfield-site"]
    result = get_entity_search(params)
    assert 2 == result["count_all"]
    for e in result["entities"]:
        assert e.dataset in ["greenspace", "brownfield-site"]
        assert "geography" == e.typology


def test_search_entity_by_date_since(test_data):
    params = raw_params.copy()
    params["entry_date_year"] = 2019
    params["entry_date_month"] = 1
    params["entry_date_day"] = 1
    params["entry_date_match"] = "since"

    result = get_entity_search(params)
    assert 4 == result["count_all"]
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
    assert 3 == result["count_all"]
    for e in result["entities"]:
        assert e.dataset in ["forest", "brownfield-site", "historical-monument"]
        assert e.dataset != "greenspace"

    params["entry_date_year"] = 2021
    result = get_entity_search(params)
    assert 2 == result["count_all"]
    for e in result["entities"]:
        assert e.dataset in ["brownfield-site", "historical-monument"]
        assert e.dataset not in ["greenspace", "forest"]

    params["entry_date_year"] = 2022
    result = get_entity_search(params)
    assert 1 == result["count_all"]
    for e in result["entities"]:
        assert e.dataset in ["historical-monument"]
        assert e.dataset not in ["greenspace", "forest", "brownfield-site"]

    params["entry_date_year"] = 2023
    result = get_entity_search(params)
    assert 0 == result["count_all"]


def test_search_entity_by_date_before(test_data):

    params = raw_params.copy()
    params["entry_date_year"] = 2019
    params["entry_date_month"] = 1
    params["entry_date_day"] = 1
    params["entry_date_match"] = "before"

    result = get_entity_search(params)
    assert 0 == result["count_all"]

    params["entry_date_year"] = 2020
    result = get_entity_search(params)
    assert 1 == result["count_all"]

    params["entry_date_year"] = 2021
    result = get_entity_search(params)
    assert 2 == result["count_all"]

    params["entry_date_year"] = 2022
    result = get_entity_search(params)
    assert 3 == result["count_all"]

    params["entry_date_year"] = 2023
    result = get_entity_search(params)
    assert 4 == result["count_all"]
    for e in result["entities"]:
        assert e.dataset in [
            "greenspace",
            "forest",
            "brownfield-site",
            "historical-monument",
        ]


def test_search_entity_by_date_equal(test_data):

    params = raw_params.copy()
    params["entry_date_year"] = 2019
    params["entry_date_month"] = 1
    params["entry_date_day"] = 1

    result = get_entity_search(params)
    assert 0 == result["count_all"]

    params["entry_date_day"] = 7

    result = get_entity_search(params)
    assert 1 == result["count_all"]
    entity = result["entities"][0]
    assert "greenspace" == entity.dataset
