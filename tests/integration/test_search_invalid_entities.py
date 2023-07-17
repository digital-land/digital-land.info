import pytest
from sqlalchemy.orm import Session

from application.data_access.entity_queries import get_entity_search
from application.db.models import EntityOrm
from application.search.enum import EntriesOption, GeometryRelation
from tests.test_data.wkt_data import handrians_wall_search


@pytest.fixture(scope="module")
def invalid_test_data(apply_migrations, db_session: Session):
    from tests.test_data import invalid_geometry

    entity_models = []
    for entity in invalid_geometry:
        e = EntityOrm(**entity)
        db_session.add(e)
        entity_models.append(e)

    db_session.commit()
    return {"entities": invalid_geometry}


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


def test_search_geometry_reference_excludes_invalid_data(invalid_test_data, params):
    invalid = [
        int(entity["entity"])
        for entity in invalid_test_data["entities"]
        if "invalid" in entity["name"]
    ]
    valid = [
        int(entity["entity"])
        for entity in invalid_test_data["entities"]
        if "invalid" not in entity["name"]
    ]
    params["geometry_reference"] = ["E07000004"]
    result = get_entity_search(params)
    for e in result["entities"]:
        assert e.entity not in invalid
        assert e.entity in valid


def test_search_by_dataset_and_lasso_excludes_invalid_geometry(
    invalid_test_data, params
):
    params["dataset"] = ["world-heritage-site"]
    params["geometry_relation"] = GeometryRelation.intersects.name
    params["geometry"] = [handrians_wall_search]
    result = get_entity_search(params)
    assert 0 == result["count"]
    assert 0 == len(result["entities"])
