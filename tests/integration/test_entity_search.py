import pytest
from datetime import datetime

from application.core.models import EntityModel
from application.data_access.entity_queries import get_entity_search
from application.search.enum import PeriodOption, GeometryRelation
from tests.test_data.wkt_data import (
    intersects_with_brownfield_entity as brownfield,
    intersects_with_greenspace_entity as greenspace,
    covers_historical_monument_entity,
    crosses_historical_entity,
    contained_by_greenspace_entity,
    touches_forest_entity,
    equals_brownfield_site_entity,
    no_intersection,
)


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

    payload = response.json()
    assert len(payload["detail"]) == 1
    detail = payload["detail"][0]
    expected_dataset_names = [d["dataset"] for d in test_data["datasets"]]

    assert detail["loc"] == ["query", "dataset"]
    assert detail["type"] == "value_error"
    assert set(detail["ctx"]["dataset_names"]) == set(expected_dataset_names)
    assert "Requested datasets do not exist: not-exists." in detail["msg"]


def test_search_entity_by_dataset_names_not_in_system_returns_only_missing(
    test_data, client, exclude_middleware
):
    response = client.get("/entity.json?dataset=not-exists&dataset=greenspace")
    assert response.status_code == 422

    detail = response.json()["detail"][0]
    expected_dataset_names = [d["dataset"] for d in test_data["datasets"]]

    assert detail["loc"] == ["query", "dataset"]
    assert detail["type"] == "value_error"
    assert set(detail["ctx"]["dataset_names"]) == set(expected_dataset_names)
    assert "Requested datasets do not exist: not-exists." in detail["msg"]


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
    assert result["count"] == 2

    for entity in result["entities"]:
        assert entity.dataset in ["greenspace", "brownfield-site"]
        assert entity.typology == "geography"


def test_search_entity_by_date_since(test_data, params, db_session):
    def count_entities_since_year(target_year):
        # entity = {"entry_date": "2020-01-07"}
        # ["2020", "01", "07"]
        # 2020
        # 2020 >= target_year
        return len(
            [
                entity
                for entity in test_data["entities"]
                if entity.get("entry_date")
                and int(entity.get("entry_date").split("-")[0]) >= target_year
            ]
        )

    entities_dataset = [entity["dataset"] for entity in test_data["entities"]]

    params["entry_date_year"] = 2019
    params["entry_date_month"] = 1
    params["entry_date_day"] = 1
    params["entry_date_match"] = "since"
    result = get_entity_search(db_session, params)

    # Check the total number of entities matches
    assert result["count"] == count_entities_since_year(params["entry_date_year"])

    for entity in result["entities"]:
        assert entity.dataset in entities_dataset
    params["entry_date_year"] = 2020
    result = get_entity_search(db_session, params)

    assert result["count"] == count_entities_since_year(params["entry_date_year"])

    for e in result["entities"]:
        assert e.dataset != "greenspace"
    params["entry_date_year"] = 2023
    result = get_entity_search(db_session, params)

    assert result["count"] == count_entities_since_year(params["entry_date_year"])


def test_search_entity_by_date_before(test_data, params, db_session):
    def count_entities_before_year(target_year):
        # entity = {"entry_date": "2020-01-07"}
        # ["2020", "01", "07"]
        # 2020
        # 2020 <= target_year
        return len(
            [
                entity
                for entity in test_data["entities"]
                if entity.get("entry_date")
                and int(entity.get("entry_date").split("-")[0]) < target_year
            ]
        )

    entities_dataset = set(e["dataset"] for e in test_data["entities"])

    params["entry_date_year"] = 2019
    params["entry_date_month"] = 1
    params["entry_date_day"] = 1
    params["entry_date_match"] = "before"

    result = get_entity_search(db_session, params)
    assert result["count"] == count_entities_before_year(params["entry_date_year"])

    params["entry_date_year"] = 2020
    result = get_entity_search(db_session, params)
    assert result["count"] == count_entities_before_year(params["entry_date_year"])

    params["entry_date_year"] = 2021
    result = get_entity_search(db_session, params)
    assert result["count"] == count_entities_before_year(params["entry_date_year"])

    # Use a date far in the future to include all entities
    params["entry_date_year"] = 2030
    result = get_entity_search(db_session, params)
    assert result["count"] == len(test_data["entities"])
    for e in result["entities"]:
        assert e.dataset in entities_dataset


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
    params["geometry"] = [brownfield]
    params["geometry_relation"] = GeometryRelation.intersects.name

    result = get_entity_search(db_session, params)
    # At least one result should be brownfield-site
    assert result["count"] >= 1
    result_datasets = [e.dataset for e in result["entities"]]
    assert "brownfield-site" in result_datasets

    params["geometry"] = [greenspace]
    result = get_entity_search(db_session, params)
    assert result["count"] >= 1
    result_datasets = [e.dataset for e in result["entities"]]
    assert "greenspace" in result_datasets


def test_search_entity_by_list_of_polygons_that_intersect(
    test_data, params, db_session
):
    params["geometry"] = [brownfield, greenspace]
    params["geometry_relation"] = GeometryRelation.intersects.name

    result = get_entity_search(db_session, params)
    # Should find at least brownfield-site and greenspace
    assert result["count"] >= 2
    result_datasets = [e.dataset for e in result["entities"]]
    assert "brownfield-site" in result_datasets
    assert "greenspace" in result_datasets


def test_search_entity_by_polygon_with_no_intersection(test_data, params, db_session):
    params["geometry"] = [no_intersection]
    params["geometry_relation"] = GeometryRelation.intersects.name

    result = get_entity_search(db_session, params)
    assert 0 == result["count"]


def test_search_all_entities(test_data, params, db_session):
    # default is PeriodOption.all - already in params
    expected_datasets = set(e["dataset"] for e in test_data["entities"])
    result = get_entity_search(db_session, params)
    assert result["count"] == len(test_data["entities"])
    for e in result["entities"]:
        assert e.dataset in expected_datasets


def test_search_current_entries(test_data, params, db_session):
    # entries without an end date
    params["period"] = [PeriodOption.current]

    # Count entities that don't have an end_date (current entries)
    today = datetime.now().date()
    current_entities = [
        e
        for e in test_data["entities"]
        if (not e.get("end_date"))
        or datetime.fromisoformat(e["end_date"]).date() > today
    ]
    expected_entities_datasets = [entity["dataset"] for entity in current_entities]

    result = get_entity_search(db_session, params)
    assert result["count"] == len(current_entities)
    for entity in result["entities"]:
        assert entity.dataset in expected_entities_datasets


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
    params["geometry"] = [equals_brownfield_site_entity]
    params["geometry_relation"] = GeometryRelation.equals.name

    result = get_entity_search(db_session, params)
    # Entities with same geometry will match
    assert result["count"] >= 1
    result_datasets = [entity.dataset for entity in result["entities"]]
    assert "brownfield-site" in result_datasets


def test_search_entity_disjoint_from_a_polygon(test_data, params, db_session):
    # Use a polygon that intersects at least one entity so the
    # disjoint/intersect partition check is meaningful
    params_intersect = params.copy()
    params_intersect["geometry"] = [brownfield]
    params_intersect["geometry_relation"] = GeometryRelation.intersects.name
    intersect_result = get_entity_search(db_session, params_intersect)
    intersect_entity_ids = {e.entity for e in intersect_result["entities"]}
    assert intersect_entity_ids  # sanity: probe actually found something

    # Test disjoint with the same geometry
    params["geometry"] = [brownfield]
    params["geometry_relation"] = GeometryRelation.disjoint.name
    disjoint_result = get_entity_search(db_session, params)
    disjoint_entity_ids = {e.entity for e in disjoint_result["entities"]}

    # Should return some disjoint entities
    assert (
        disjoint_result["count"] > 0
    ), "Should find entities disjoint from brownfield polygon"

    # Get all entities with geometry for comparison
    params_all = params.copy()
    del params_all["geometry"]
    del params_all["geometry_relation"]
    params_all["limit"] = 100
    all_result = get_entity_search(db_session, params_all)
    all_entities_with_geometry = {
        e.entity for e in all_result["entities"] if e.geometry is not None
    }

    union_results = intersect_entity_ids.union(disjoint_entity_ids)
    coverage_ratio = len(union_results) / len(all_entities_with_geometry)
    assert (
        coverage_ratio >= 0.5
    ), f"Spatial queries should cover reasonable portion of entities with geometry (got {coverage_ratio:.2f})"

    # Assert that the two queries return different meaningful results
    assert (
        len(intersect_entity_ids) > 0
    ), "Should have entities intersecting with brownfield"
    assert len(disjoint_entity_ids) > 0, "Should have entities disjoint from brownfield"
    assert (
        intersect_entity_ids != disjoint_entity_ids
    ), "Intersect and disjoint should return different results"


def test_search_entity_that_polygon_touches(test_data, params, mocker, db_session):
    params["geometry"] = [touches_forest_entity]
    params["geometry_relation"] = GeometryRelation.touches.name

    result = get_entity_search(db_session, params)
    assert result["count"] == 1
    assert result["entities"][0].dataset == "forest"


def test_search_entity_that_contains_a_polygon(test_data, params, db_session):
    params["geometry"] = [contained_by_greenspace_entity]
    params["geometry_relation"] = GeometryRelation.contains.name

    result = get_entity_search(db_session, params)
    assert result["count"] == 1
    assert result["entities"][0].dataset == "greenspace"


# when dealing with polygons contains and covers are synonymous
def test_search_entity_that_covers_a_polygon(test_data, params, db_session):
    params["geometry"] = [contained_by_greenspace_entity]
    params["geometry_relation"] = GeometryRelation.covers.name

    result = get_entity_search(db_session, params)
    assert result["count"] == 1
    assert result["entities"][0].dataset == "greenspace"


def test_search_entity_covered_by_a_polygon(test_data, params, db_session):
    params["geometry"] = [covers_historical_monument_entity]
    params["geometry_relation"] = GeometryRelation.coveredby.name
    result = get_entity_search(db_session, params)

    assert result["count"] == 1
    assert result["entities"][0].dataset == "historical-monument"


def test_search_entity_that_overlaps_a_polygon(test_data, params, db_session):
    params["geometry"] = [brownfield]
    params["geometry_relation"] = GeometryRelation.overlaps.name

    result = get_entity_search(db_session, params)
    # Entities with same geometry as brownfield will match
    assert result["count"] >= 1
    result_datasets = [entity.dataset for entity in result["entities"]]
    assert "brownfield-site" in result_datasets


def test_search_entity_that_is_crossed_by_a_line(test_data, params, db_session):
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


def test_search_entity_with_exclude_parameter(test_data, params, db_session):
    params["geometry"] = [brownfield, greenspace]
    params["geometry_relation"] = GeometryRelation.intersects.name
    params["exclude_field"] = [""]

    result = get_entity_search(db_session, params)
    initial_count = result["count"]

    for entity in result["entities"]:
        assert entity.geometry is not None
    # Should find at least brownfield-site and greenspace
    assert initial_count >= 2

    result_datasets = [e.dataset for e in result["entities"]]
    assert "brownfield-site" in result_datasets
    assert "greenspace" in result_datasets

    params["exclude_field"] = ["geometry"]
    result = get_entity_search(db_session, params)
    for entity in result["entities"]:
        assert entity.geometry is None

    # Count should remain the same when excluding geometry field
    assert result["count"] == initial_count


# TODO test cases for contains, within


WHOLE_WORLD = "POLYGON((-180 -90,180 -90,180 90,-180 90,-180 -90))"


def _whole_world_search(params, **overrides):
    return {
        **params,
        "geometry": [WHOLE_WORLD],
        "geometry_relation": GeometryRelation.intersects,
        **overrides,
    }


def test_capped_search_at_or_below_cap_returns_complete_sorted_pages(
    test_data, params, db_session, mocker
):
    everything = get_entity_search(db_session, _whole_world_search(params, limit=500))
    total = everything["count"]
    assert total > 2
    ids = [entity.entity for entity in everything["entities"]]
    assert ids == sorted(ids) and len(ids) == total

    mocker.patch(
        "application.data_access.entity_queries.ENTITY_SEARCH_COUNT_CAP", total
    )
    second_page = get_entity_search(
        db_session, _whole_world_search(params, limit=1, offset=1)
    )
    assert second_page["count"] == total
    assert second_page["count_is_capped"] is False
    assert [entity.entity for entity in second_page["entities"]] == [ids[1]]


def test_capped_search_above_cap_returns_one_page_only(
    test_data, params, db_session, mocker
):
    mocker.patch("application.data_access.entity_queries.ENTITY_SEARCH_COUNT_CAP", 2)
    first = get_entity_search(db_session, _whole_world_search(params, limit=2))
    assert first["count"] == 2
    assert first["count_is_capped"] is True
    assert len(first["entities"]) == 2

    later = get_entity_search(
        db_session, _whole_world_search(params, limit=2, offset=2)
    )
    assert later["count"] == 2
    assert later["count_is_capped"] is True
    assert later["entities"] == []


def test_direct_filter_matches_original_filter(test_data, params, db_session):
    from application.data_access.entity_queries import (
        _apply_base_filters,
        _apply_location_filters,
    )
    from application.data_access.entity_query_helpers import normalised_params
    from application.db.models import EntityOrm

    for polygon in (brownfield, greenspace, no_intersection, WHOLE_WORLD):
        search = _whole_world_search(params, geometry=[polygon], limit=500)
        direct = get_entity_search(db_session, search)
        normalised = normalised_params(search)
        original = _apply_location_filters(
            db_session,
            _apply_base_filters(db_session.query(EntityOrm), normalised),
            normalised,
        ).order_by(EntityOrm.entity)
        assert [entity.entity for entity in direct["entities"]] == [
            row.entity for row in original
        ]


def test_search_timeout_is_reported_and_session_stays_usable(db_session, mocker):
    from sqlalchemy import func, text
    from application.data_access.entity_queries import (
        EntitySearchTooBroad,
        _fetch_with_search_timeout,
    )

    settings = mocker.Mock(
        ENTITY_SEARCH_STATEMENT_TIMEOUT_MS=50, DB_STATEMENT_TIMEOUT_MS=60000
    )
    mocker.patch(
        "application.data_access.entity_queries.get_settings", return_value=settings
    )
    with pytest.raises(EntitySearchTooBroad):
        _fetch_with_search_timeout(db_session, db_session.query(func.pg_sleep(1)))
    assert db_session.execute(text("SELECT 1")).scalar() == 1

    _fetch_with_search_timeout(db_session, db_session.query(func.pg_sleep(0)))
    assert db_session.execute(text("SHOW statement_timeout")).scalar() == "1min"
    db_session.rollback()


def test_capped_geojson_search_reports_count_and_cap_flag(
    test_data, client, exclude_middleware, mocker
):
    mocker.patch("application.data_access.entity_queries.ENTITY_SEARCH_COUNT_CAP", 2)
    response = client.get(
        "/entity.geojson",
        params={
            "geometry": WHOLE_WORLD,
            "geometry_relation": "intersects",
            "limit": 2,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"
    assert data["count"] == 2
    assert data["count_is_capped"] is True
    assert "next" not in data["links"]
