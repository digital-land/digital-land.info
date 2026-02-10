import logging
import pytest
from application.data_access.entity_query_helpers import normalised_params
from dataclasses import asdict
from bs4 import BeautifulSoup
from urllib.parse import parse_qsl

from application.routers.entity import (
    _get_entity_json,
    _get_geojson,
    get_entity,
    search_entities,
)

from fastapi.exceptions import HTTPException

from unittest.mock import MagicMock

from application.core.models import (
    EntityModel,
    DatasetModel,
    GeoJSON,
    OrganisationModel,
    TypologyModel,
)
from application.search.filters import QueryFilters


from fastapi.responses import RedirectResponse


@pytest.fixture
def multiple_entity_models():
    model_1 = EntityModel(
        entity=11000000,
        entry_date="2022-03-23",
        name="Abbotswood Shaw",
        reference="1481207",
        dataset="ancient-woodland",
        prefix="ancient-woodland",
        geojson={
            "type": "Feature",
            "geometry": {
                "type": "MultiPolygon",
                "coordinates": [
                    [
                        [
                            [0.145139, 50.986737],
                            [0.145088, 50.986778],
                            [0.14473, 50.986668],
                            [0.145139, 50.986737],
                        ]
                    ]
                ],
            },
        },
    )

    model_2 = EntityModel(
        entity=11000000,
        entry_date="2022-03-23",
        name="Abbotswood Shaw",
        reference="1481207",
        dataset="ancient-woodland",
        prefix="ancient-woodland",
        geojson={
            "type": "Feature",
            "geometry": {
                "type": "MultiPolygon",
                "coordinates": [
                    [
                        [
                            [0.145139, 50.986737],
                            [0.145088, 50.986778],
                            [0.14473, 50.986668],
                            [0.145139, 50.986737],
                        ]
                    ]
                ],
            },
        },
    )

    return [model_1, model_2]


def test__get_geojson_multiple_entity_models_provided(multiple_entity_models):
    result = _get_geojson(multiple_entity_models)
    assert "type" in result, "expecting geojson structure to have type attribute"
    assert result["type"] == "FeatureCollection"
    assert "features" in result, "expected features attribute"


def test__get_entity_json_multiple_entity_models_provided_nothing_included(
    multiple_entity_models,
):
    result = _get_entity_json(multiple_entity_models)
    assert isinstance(result, list), f"{type(result)} returned when a list was ecpected"
    for entity in result:
        assert "geojson" not in entity, f"geojson found in {entity.keys()}"


def test__get_entity_json_multiple_entity_models_provided_include_value_not_in_model(
    multiple_entity_models,
):
    result = _get_entity_json(multiple_entity_models, include={"value-not-in-entity"})
    assert isinstance(result, list), f"{type(result)} returned when a list was ecpected"
    logging.warning(result)
    for entity in result:
        assert "entity" in entity, f"entity found in {entity.keys()}"
        assert len(entity.keys()) == 1, f"expected only entity not {entity.keys()}"


def test__get_entity_json_multiple_entity_models_provided_include_value_in_model(
    multiple_entity_models,
):
    result = _get_entity_json(multiple_entity_models, include={"name"})
    assert isinstance(result, list), f"{type(result)} returned when a list was ecpected"
    for entity in result:
        assert (
            "entity" in entity and "name" in entity
        ), f"expected entity and name not {entity.keys()}"
        assert len(entity.keys()) == 2, f"expected entity and name not {entity.keys()}"


def test_get_geojson_with_exclude_fields(multiple_entity_models):
    exclude_fields = {"notes"}
    geojson_data = _get_geojson(multiple_entity_models, exclude=exclude_fields)

    assert len(geojson_data["features"]) == 2
    for feature in geojson_data["features"]:
        assert "notes" not in feature.properties


def test_get_geojson_without_exclude_fields(multiple_entity_models):
    exclude_fields = None
    geojson_data = _get_geojson(multiple_entity_models, exclude=exclude_fields)

    assert len(geojson_data["features"]) == 2
    for feature in geojson_data["features"]:
        assert "prefix" in feature.properties
        assert "name" in feature.properties


def test_get_geojson_with_multiple_exclude_fields(multiple_entity_models):
    exclude_fields = {"prefix", "geometry"}
    geojson_data = _get_geojson(multiple_entity_models, exclude=exclude_fields)

    assert len(geojson_data["features"]) == 2
    for feature in geojson_data["features"]:
        assert "prefix" not in feature.properties
        assert "geometry" not in feature.properties


def test_get_entity_json_with_exclude_fields(multiple_entity_models):
    exclude_fields = {"geometry"}
    entities = _get_entity_json(multiple_entity_models, exclude=exclude_fields)

    assert len(entities) == 2
    for entity in entities:
        assert "geometry" not in entity


def test_get_entity_json_without_exclude_fields(multiple_entity_models):
    exclude_fields = None
    entities = _get_entity_json(multiple_entity_models, exclude=exclude_fields)

    assert len(entities) == 2
    for entity in entities:
        assert "geometry" in entity
        assert "name" in entity


def test_get_entity_json_with_multiple_exclude_fields(multiple_entity_models):
    exclude_fields = {"prefix", "geometry"}
    entities = _get_entity_json(multiple_entity_models, exclude=exclude_fields)

    assert len(entities) == 2
    for entity in entities:
        assert ("prefix", "geometry") not in entity


def test_get_entity_no_entity_returned_html(mocker):
    mocker.patch(
        "application.routers.entity.get_entity_query", return_value=(None, None, None)
    )
    mocker.patch(
        "application.routers.entity.get_dataset_names",
        return_value=["ancient-woodland"],
    )
    request = MagicMock()
    try:
        get_entity(
            request=request,
            entity="11000000",
            extension=None,
        )
        assert False, "Expected HTTPException to be raised"
    except HTTPException:
        assert True


def test_get_entity_no_entity_returned_json(mocker):
    mocker.patch(
        "application.routers.entity.get_entity_query", return_value=(None, None, None)
    )
    request = MagicMock()
    extension = MagicMock()
    extension.value = "json"
    try:
        get_entity(
            request=request,
            entity="11000000",
            extension=extension,
        )
        assert False, "Expected HTTPException to be raised"
    except HTTPException:
        assert True


def test_get_entity_no_entity_returned_geojson(mocker):
    mocker.patch(
        "application.routers.entity.get_entity_query", return_value=(None, None, None)
    )
    request = MagicMock()
    extension = MagicMock()
    extension.value = "geojson"
    try:
        get_entity(
            request=request,
            entity="11000000",
            extension=extension,
        )
        assert False, "Expected HTTPException to be raised"
    except HTTPException:
        assert True


def test_get_entity_old_entity_gone_returned_html(mocker):
    mocker.patch(
        "application.routers.entity.get_entity_query", return_value=(None, 410, None)
    )
    request = MagicMock()
    result = get_entity(request=request, entity="11000000", extension=None)
    try:
        result.template.render(result.context)
        assert True
    except Exception:
        if hasattr(result, "context"):
            logging.warning(f"context: {result.context}")
        else:
            logging.warning("result has no context")
        assert False, "template unable to render, missing variable(s) from context"


def test_get_entity_old_entity_gone_returned_json(mocker):
    mocker.patch(
        "application.routers.entity.get_entity_query", return_value=(None, 410, None)
    )
    request = MagicMock()
    extension = MagicMock()
    extension.value = "json"
    try:
        get_entity(request=request, entity="11000000", extension=extension)
        assert False, "Expected HTTPException to be raised"
    except HTTPException:
        assert True


def test_get_entity_old_entity_gone_returned_geojson(mocker):
    mocker.patch(
        "application.routers.entity.get_entity_query", return_value=(None, 410, None)
    )
    request = MagicMock()
    extension = MagicMock()
    extension.value = "geojson"
    try:
        get_entity(request=request, entity="11000000", extension=extension)
        assert False, "Expected HTTPException to be raised"
    except HTTPException:
        assert True


def test_get_entity_old_entity_redirect_returned_html(mocker):
    mocker.patch(
        "application.routers.entity.get_entity_query", return_value=(None, 301, 1100000)
    )
    request = MagicMock()
    result = get_entity(request=request, entity="11000000", extension=None)
    assert isinstance(
        result, RedirectResponse
    ), f"expected a redirect response not {type(result)}"


def test_get_entity_old_entity_redirect_returned_json(mocker):
    mocker.patch(
        "application.routers.entity.get_entity_query", return_value=(None, 301, 1100000)
    )
    request = MagicMock()
    extension = MagicMock()
    extension.value = "json"
    result = get_entity(request=request, entity="11000000", extension=extension)
    assert isinstance(
        result, RedirectResponse
    ), f"expected a redirect response not {type(result)}"


def test_get_entity_old_entity_redirect_returned_geojson(mocker):
    mocker.patch(
        "application.routers.entity.get_entity_query", return_value=(None, 301, 1100000)
    )
    request = MagicMock()
    extension = MagicMock()
    extension.value = "geojson"
    result = get_entity(request=request, entity="11000000", extension=extension)
    assert isinstance(
        result, RedirectResponse
    ), f"expected a redirect response not {type(result)}"


@pytest.fixture
def single_entity_model():
    model = EntityModel(
        entity=11000000,
        entry_date="2022-03-23",
        name="Abbotswood Shaw",
        reference="1481207",
        dataset="ancient-woodland",
        prefix="ancient-woodland",
        geojson={
            "type": "Feature",
            "geometry": {
                "type": "MultiPolygon",
                "coordinates": [
                    [
                        [
                            [0.145139, 50.986737],
                            [0.145088, 50.986778],
                            [0.14473, 50.986668],
                            [0.145139, 50.986737],
                        ]
                    ]
                ],
            },
        },
    )
    return model


@pytest.fixture
def linked_entity_model():
    model = EntityModel(
        entity=4220006,
        entry_date="2022-03-23",
        name="test Local Plan",
        reference="1481207",
        dataset="local-plan",
        prefix="local-plan",
        json={
            "adopted-date": "2018-09-27",
            "documentation-url": "https://www.scambs.gov.uk/planning/south-cambridgeshire-local-plan-2018",
            "local-plan-boundary": "E07000012",
        },
    )
    return model, None


@pytest.fixture
def ancient_woodland_dataset():
    return DatasetModel(
        collection="ancient-woodland",
        dataset="ancient-woodland",
        name="Ancient woodland",
        plural="Ancient woodlands",
        typology="geography",
        paint_options={"colour": "#78AA00"},
    )


@pytest.fixture
def local_plan_boundary_dataset():
    return DatasetModel(
        collection="local-plan",
        dataset="local-plan-boundary",
        name="Local plan boundary",
        plural="Local plan boundaries",
        typology="geography",
        paint_options={"colour": "#78AA00"},
    )


@pytest.fixture
def historic_england_dataset():
    return DatasetModel(
        collection="historic-england",
        dataset="battlefield",
        name="Battlefield",
        plural="Battlefields",
        typology="geography",
    )


@pytest.fixture
def multiple_dataset_models(ancient_woodland_dataset, historic_england_dataset):
    return [ancient_woodland_dataset, historic_england_dataset]


@pytest.fixture
def local_plan_dataset_model():
    model = EntityModel(
        entity=4219999,
        entry_date="2022-03-23",
        name="South Cambridgeshire District Council",
        reference="E07000012",
        dataset="local-plan-boundary",
        prefix="local-plan-boundary",
        geojson={
            "type": "Feature",
            "geometry": {
                "type": "MultiPolygon",
                "coordinates": [
                    [
                        [
                            [0.145139, 50.986737],
                            [0.145088, 50.986778],
                            [0.14473, 50.986668],
                            [0.145139, 50.986737],
                        ]
                    ]
                ],
            },
        },
    )
    return model


def test_get_entity_entity_returned_html(
    mocker, single_entity_model, multiple_dataset_models, ancient_woodland_dataset
):
    mocker.patch(
        "application.routers.entity.get_entity_query",
        return_value=(single_entity_model, None, None),
    )
    mocker.patch(
        "application.routers.entity.get_datasets", return_value=multiple_dataset_models
    )
    mocker.patch(
        "application.routers.entity.get_dataset_query",
        return_value=ancient_woodland_dataset,
    )

    request = MagicMock()
    result = get_entity(request=request, entity="11000000", extension=None)

    assert (
        result.status_code == 200
    ), f"result status code should be 200 not {result.status_code}"
    try:
        result.template.render(result.context)
        assert True
    except Exception:
        if hasattr(result, "context"):
            logging.warning(f"context: {result.context}")
        else:
            logging.warning("result has no context")
        assert False, "template unable to render, missing variable(s) from context"


def test_get_entity_entity_returned_json(
    mocker, single_entity_model, multiple_dataset_models, ancient_woodland_dataset
):
    mocker.patch(
        "application.routers.entity.get_entity_query",
        return_value=(single_entity_model, None, None),
    )
    mocker.patch(
        "application.routers.entity.get_datasets", return_value=multiple_dataset_models
    )
    mocker.patch(
        "application.routers.entity.get_dataset_query",
        return_value=ancient_woodland_dataset,
    )
    request = MagicMock()
    extension = MagicMock()
    extension.value = "json"
    result = get_entity(request=request, entity="11000000", extension=extension)

    assert isinstance(
        result, dict
    ), f"{type(result)} is expected to be a python dictionary"
    assert "geojson" not in result, "geojson in result dict"


def test_get_entity_entity_returned_geojson(
    mocker, single_entity_model, multiple_dataset_models, ancient_woodland_dataset
):
    mocker.patch(
        "application.routers.entity.get_entity_query",
        return_value=(single_entity_model, None, None),
    )
    mocker.patch(
        "application.routers.entity.get_datasets", return_value=multiple_dataset_models
    )
    mocker.patch(
        "application.routers.entity.get_dataset_query",
        return_value=ancient_woodland_dataset,
    )
    request = MagicMock()
    extension = MagicMock()
    extension.value = "geojson"
    result = get_entity(request=request, entity="11000000", extension=extension)
    assert isinstance(result, GeoJSON), f"{type(result)} is expected to be a GeoJSON"


# @pytest.fixture
# def query_params():
#     QueryFilters(

#     )


@pytest.fixture
def typologies():
    model_1 = TypologyModel(typology="category", name="Category", plura="Categories")
    model_2 = TypologyModel(typology="geography", name="Geography", plura="geographies")
    return [model_1, model_2]


@pytest.fixture
def local_authorities():
    model_1 = OrganisationModel(
        organisation="local-authority-eng:ADU",
        name="Adur District Council",
        statistical_geography="E07000223",
    )
    model_2 = OrganisationModel(
        organisation="local-authority-eng:ALL",
        name="Allerdale Borough Council",
        statistical_geography="E07000026",
    )
    return [model_1, model_2]


@pytest.fixture
def organisation_list():
    org_model_1 = EntityModel(
        entry_date="2022-03-23",
        start_date=None,
        end_date=None,
        entity=4211001,
        name="London Borough of Islington",
        dataset="local-plan-boundary",
        typology="geography",
        reference="E09000019",
        prefix="local-plan-boundary",
        organisation_entity="600001",
        geojson=GeoJSON(
            geometry={
                "type": "MultiPolygon",
                "coordinates": [[[[-0.119213, 51.574996], [-0.119513, 51.575511]]]],
            }
        ),
        geometry="MULTIPOLYGON (((-0.119213 51.574996, ...)))",
        point="POINT (-0.110224 51.548489)",
        organisations="local-authority:ISL",
        plan_boundary_type="statistical-geography",
    )
    org_model_2 = EntityModel(
        entry_date="2024-07-10",
        start_date="2006-05-01",
        end_date="2021-09-20",
        entity=12,
        name="Ministry of Housing, Communities and Local Government",
        dataset="government-organisation",
        typology="organisation",
        reference="D4",
        prefix="government-organisation",
        organisation_entity="600001",
        geojson=None,
        geometry=None,
        point=None,
        twitter="mhclg",
        website="https://www.gov.uk/government/organisations/ministry-of-housing-communities-and-local-government",
        wikidata="Q601819",
        wikipedia="Department_for_Levelling_Up,_Housing_and_Communities",
        parliament_thesaurus="442434",
        opendatacommunities_uri="None",
    )
    return [org_model_1, org_model_2]


def test_search_entities_no_entities_returned_no_query_params_html(
    mocker, typologies, local_authorities, multiple_dataset_models, organisation_list
):
    normalised_query_params = normalised_params(asdict(QueryFilters()))
    mocker.patch(
        "application.routers.entity.get_entity_search",
        return_value={"params": normalised_query_params, "count": 0, "entities": []},
    )
    mocker.patch(
        "application.routers.entity.get_datasets", return_value=multiple_dataset_models
    )
    mocker.patch(
        "application.routers.entity.get_all_datasets",
        return_value=multiple_dataset_models,
    )
    mocker.patch(
        "application.routers.entity.get_typologies_with_entities",
        return_value=typologies,
    )
    mocker.patch(
        "application.routers.entity.get_local_authorities",
        return_value=local_authorities,
    )
    mocker.patch(
        "application.routers.entity.get_dataset_names",
        return_value=["ancient-woodland"],
    )
    mocker.patch(
        "application.routers.entity.get_typology_names", return_value=["geography"]
    )
    mocker.patch(
        "application.routers.entity.get_organisations", return_value=organisation_list
    )

    request = MagicMock()
    result = search_entities(
        request=request,
        search_query="",
        query_filters=QueryFilters(),
        extension=None,
    )
    try:
        result.template.render(result.context)
        assert True
    except Exception:
        if hasattr(result, "context"):
            logging.warning(f"context: {result.context}")
        else:
            logging.warning("result has no context")
        assert False, "template unable to render, missing variable(s) from context"


def test_search_entities_no_entities_returned_no_query_params_json(mocker):
    normalised_query_params = normalised_params(asdict(QueryFilters()))
    mocker.patch(
        "application.routers.entity.get_entity_search",
        return_value={"params": normalised_query_params, "count": 0, "entities": []},
    )
    mocker.patch(
        "application.routers.entity.get_dataset_names",
        return_value=["ancient-woodland"],
    )
    mocker.patch(
        "application.routers.entity.get_typology_names", return_value=["geography"]
    )

    request = MagicMock()
    request.query_params.get.return_value = None
    extension = MagicMock()
    extension.value = "json"
    result = search_entities(
        request=request,
        search_query="",
        query_filters=QueryFilters(),
        extension=extension,
    )
    assert isinstance(
        result, dict
    ), f"{type(result)} is expected to be a python dictionary"
    for key in ["entities", "links", "count"]:
        assert key in result.keys(), f"{key} missing from result"


def test_search_entities_no_entities_returned_no_query_params_geojson(mocker):
    normalised_query_params = normalised_params(asdict(QueryFilters()))
    mocker.patch(
        "application.routers.entity.get_entity_search",
        return_value={"params": normalised_query_params, "count": 0, "entities": []},
    )
    mocker.patch(
        "application.routers.entity.get_dataset_names",
        return_value=["ancient-woodland"],
    )
    mocker.patch(
        "application.routers.entity.get_typology_names", return_value=["geography"]
    )
    request = MagicMock()
    request.query_params.get.return_value = None
    extension = MagicMock()
    extension.value = "geojson"
    result = search_entities(
        request=request,
        search_query="",
        query_filters=QueryFilters(),
        extension=extension,
    )
    assert isinstance(
        result, dict
    ), f"{type(result)} is expected to be a python dictionary"
    assert "type" in result, "expecting geojson structure to have type attribute"
    assert result["type"] == "FeatureCollection"
    assert "features" in result, "expected features attribute"


def test_search_entities_multiple_entities_returned_no_query_params_html(
    mocker,
    multiple_entity_models,
    typologies,
    local_authorities,
    organisation_list,
    multiple_dataset_models,
    ancient_woodland_dataset,
):
    normalised_query_params = normalised_params(asdict(QueryFilters()))
    mocker.patch(
        "application.routers.entity.get_entity_search",
        return_value={
            "params": normalised_query_params,
            "count": 2,
            "entities": multiple_entity_models,
        },
    )
    mocker.patch(
        "application.routers.entity.get_datasets", return_value=multiple_dataset_models
    )
    mocker.patch(
        "application.routers.entity.get_all_datasets",
        return_value=multiple_dataset_models,
    )
    mocker.patch(
        "application.routers.entity.get_typologies_with_entities",
        return_value=typologies,
    )
    mocker.patch(
        "application.routers.entity.get_local_authorities",
        return_value=local_authorities,
    )
    mocker.patch(
        "application.routers.entity.get_organisations", return_value=organisation_list
    )
    mocker.patch(
        "application.routers.entity.get_dataset_names",
        return_value=["ancient-woodland"],
    )
    mocker.patch(
        "application.routers.entity.get_typology_names", return_value=["geography"]
    )

    request = MagicMock()
    result = search_entities(
        request=request,
        search_query="",
        query_filters=QueryFilters(),
        extension=None,
    )
    try:
        result.template.render(result.context)
        assert True
    except Exception:
        if hasattr(result, "context"):
            logging.warning(f"context: {result.context}")
        else:
            logging.warning("result has no context")
        assert False, "template unable to render, missing variable(s) from context"


def test_search_entities_multiple_entities_returned_no_query_params_json(
    mocker, multiple_entity_models
):
    normalised_query_params = normalised_params(asdict(QueryFilters()))
    mocker.patch(
        "application.routers.entity.get_entity_search",
        return_value={
            "params": normalised_query_params,
            "count": 0,
            "entities": multiple_entity_models,
        },
    )
    mocker.patch(
        "application.routers.entity.get_dataset_names",
        return_value=["ancient-woodland"],
    )
    mocker.patch(
        "application.routers.entity.get_typology_names", return_value=["geography"]
    )
    request = MagicMock()
    request.query_params.get.return_value = None
    extension = MagicMock()
    extension.value = "json"
    result = search_entities(
        request=request,
        search_query="",
        query_filters=QueryFilters(),
        extension=extension,
    )
    assert isinstance(
        result, dict
    ), f"{type(result)} is expected to be a python dictionary"
    for key in ["entities", "links", "count"]:
        assert key in result.keys(), f"{key} missing from result"


def test_search_entities_multiple_entities_returned_no_query_params_geojson(
    mocker, multiple_entity_models
):
    normalised_query_params = normalised_params(asdict(QueryFilters()))
    mocker.patch(
        "application.routers.entity.get_entity_search",
        return_value={
            "params": normalised_query_params,
            "count": 0,
            "entities": multiple_entity_models,
        },
    )
    mocker.patch(
        "application.routers.entity.get_dataset_names",
        return_value=["ancient-woodland"],
    )
    mocker.patch(
        "application.routers.entity.get_typology_names", return_value=["geography"]
    )
    request = MagicMock()
    request.query_params.get.return_value = None
    extension = MagicMock()
    extension.value = "geojson"
    result = search_entities(
        request=request,
        search_query="",
        query_filters=QueryFilters(),
        extension=extension,
    )
    assert isinstance(
        result, dict
    ), f"{type(result)} is expected to be a python dictionary"
    assert "type" in result, "expecting geojson structure to have type attribute"
    assert result["type"] == "FeatureCollection"
    assert "features" in result, "expected features attribute"


@pytest.mark.parametrize("extension_value", [("json"), ("geojson"), (None)])
def test_search_entities_with_query_extension(
    mocker, extension_value, multiple_entity_models
):
    request = MagicMock()
    request.query_params.get.return_value = extension_value
    extension = MagicMock()
    extension.value = extension_value

    normalised_query_params = normalised_params(asdict(QueryFilters()))
    mocker.patch(
        "application.routers.entity.get_entity_search",
        return_value={
            "params": normalised_query_params,
            "count": 0,
            "entities": multiple_entity_models,
        },
    )
    mocker.patch(
        "application.routers.entity.get_dataset_names",
        return_value=["dataset1"],
    )
    mocker.patch(
        "application.routers.entity.get_typology_names",
        return_value=["typology1"],
    )
    mock_get_session = mocker.patch(
        "application.routers.entity.get_session", return_value=MagicMock()
    )

    result = search_entities(
        request=request,
        search_query="",
        query_filters=QueryFilters(),
        extension=extension,
        session=mock_get_session.return_value,
        redis=None,
    )
    try:
        result.template.render(result.context)
        assert True
    except Exception:
        if hasattr(result, "context"):
            logging.warning(f"context: {result.context}")
        else:
            logging.warning("result has no context")
            assert False, "template unable to render, missing variable(s) from context"


def test_get_entity_with_linked_local_plans(
    mocker, local_plan_dataset_model, local_plan_boundary_dataset, linked_entity_model
):
    mocker.patch(
        "application.routers.entity.get_entity_query",
        return_value=(local_plan_dataset_model, None, None),
    )
    mocker.patch(
        "application.routers.entity.get_datasets",
        return_value=[local_plan_boundary_dataset],
    )
    mocker.patch(
        "application.routers.entity.get_dataset_query",
        return_value=local_plan_boundary_dataset,
    )
    mocker.patch(
        "application.routers.entity.fetch_linked_local_plans",
        return_value=linked_entity_model,
    )

    request = MagicMock()
    result = get_entity(request=request, entity="4219999", extension=None)

    assert (
        result.status_code == 200
    ), f"result status code should be 200 not {result.status_code}"
    try:
        result.template.render(result.context)
        assert True
    except Exception:
        if hasattr(result, "context"):
            logging.warning(f"context: {result.context}")
        else:
            logging.warning("result has no context")
        assert False, "template unable to render, missing variable(s) from context"


def _mock_search_entities_html_dependencies(
    mocker,
    query_filters,
    typologies,
    local_authorities,
    organisation_list,
    multiple_dataset_models,
):
    def _mock_get_entity_search(_session, params, _extension):
        return {
            "params": normalised_params(params),
            "count": 0,
            "entities": [],
        }

    mocker.patch(
        "application.routers.entity.get_entity_search",
        side_effect=_mock_get_entity_search,
    )
    mocker.patch(
        "application.routers.entity.get_all_datasets",
        return_value=multiple_dataset_models,
    )
    mocker.patch(
        "application.routers.entity.get_typologies_with_entities",
        return_value=typologies,
    )
    mocker.patch(
        "application.routers.entity.get_local_authorities",
        return_value=local_authorities,
    )
    mocker.patch(
        "application.routers.entity.get_dataset_names",
        return_value=["conservation-area"],
    )
    mocker.patch(
        "application.routers.entity.get_typology_names",
        return_value=["geography"],
    )
    mocker.patch(
        "application.routers.entity.get_organisations",
        return_value=organisation_list,
    )


def _make_search_request(query):
    request = MagicMock()
    request.url.scheme = "https"
    request.url.netloc = "example.org"
    request.url.path = "/entity/"
    request.url.query = query
    query_param_list = parse_qsl(query, keep_blank_values=True)
    request.query_params._list = query_param_list
    query_param_map = dict(query_param_list)
    request.query_params.get.side_effect = (
        lambda key, default=None: query_param_map.get(key, default)
    )
    return request


def test_search_entities_area_chip_label_postcode(
    mocker,
    typologies,
    local_authorities,
    organisation_list,
    multiple_dataset_models,
):
    query_filters = QueryFilters(q="SW1A 1AA", dataset=["conservation-area"])
    _mock_search_entities_html_dependencies(
        mocker,
        query_filters,
        typologies,
        local_authorities,
        organisation_list,
        multiple_dataset_models,
    )
    mocker.patch(
        "application.routers.entity.find_an_area",
        return_value={
            "type": "postcode",
            "result": {"POSTCODE": "SW1A 1AA", "LAT": 51.501, "LNG": -0.141},
        },
    )

    request = _make_search_request("q=SW1A+1AA&dataset=conservation-area")
    result = search_entities(
        request=request,
        search_query="SW1A 1AA",
        query_filters=query_filters,
        extension=None,
    )
    rendered = result.template.render(result.context)

    assert "Postcode:" in rendered
    assert "UPRN:" not in rendered


def test_search_entities_area_chip_label_uprn(
    mocker,
    typologies,
    local_authorities,
    organisation_list,
    multiple_dataset_models,
):
    query_filters = QueryFilters(q="100023336956", dataset=["conservation-area"])
    _mock_search_entities_html_dependencies(
        mocker,
        query_filters,
        typologies,
        local_authorities,
        organisation_list,
        multiple_dataset_models,
    )
    mocker.patch(
        "application.routers.entity.find_an_area",
        return_value={
            "type": "uprn",
            "result": {"UPRN": "100023336956", "LAT": 51.501, "LNG": -0.141},
        },
    )

    request = _make_search_request("q=100023336956&dataset=conservation-area")
    result = search_entities(
        request=request,
        search_query="100023336956",
        query_filters=query_filters,
        extension=None,
    )
    rendered = result.template.render(result.context)

    assert "UPRN:" in rendered
    assert "Postcode:" not in rendered


def test_search_entities_area_chip_label_fallback_to_search_query_type(
    mocker,
    typologies,
    local_authorities,
    organisation_list,
    multiple_dataset_models,
):
    query_filters = QueryFilters(q="SW1A 1AA", dataset=["conservation-area"])
    _mock_search_entities_html_dependencies(
        mocker,
        query_filters,
        typologies,
        local_authorities,
        organisation_list,
        multiple_dataset_models,
    )
    mocker.patch("application.routers.entity.find_an_area", return_value=None)

    request = _make_search_request("q=SW1A+1AA&dataset=conservation-area")
    result = search_entities(
        request=request,
        search_query="SW1A 1AA",
        query_filters=query_filters,
        extension=None,
    )
    rendered = result.template.render(result.context)

    assert "Postcode:" in rendered
    assert "UPRN:" not in rendered


def test_search_entities_area_chip_remove_link_clears_area_params(
    mocker,
    typologies,
    local_authorities,
    organisation_list,
    multiple_dataset_models,
):
    query_filters = QueryFilters(
        q="SW1A 1AA",
        dataset=["conservation-area"],
        latitude=51.501,
        longitude=-0.141,
    )
    _mock_search_entities_html_dependencies(
        mocker,
        query_filters,
        typologies,
        local_authorities,
        organisation_list,
        multiple_dataset_models,
    )
    mocker.patch(
        "application.routers.entity.find_an_area",
        return_value={
            "type": "postcode",
            "result": {"POSTCODE": "SW1A 1AA", "LAT": 51.501, "LNG": -0.141},
        },
    )

    request = _make_search_request(
        "q=SW1A+1AA&dataset=conservation-area&latitude=51.501&longitude=-0.141&resolved_q=SW1A+1AA"
    )
    result = search_entities(
        request=request,
        search_query="SW1A 1AA",
        query_filters=query_filters,
        extension=None,
    )
    rendered = result.template.render(result.context)
    soup = BeautifulSoup(rendered, "html.parser")
    area_label = soup.find("span", string="Postcode:")
    assert area_label is not None
    area_group = area_label.find_parent("div", class_="app-applied-filter__group")
    assert area_group is not None
    area_link = area_group.find("a", class_="app-applied-filter__button")
    assert area_link is not None

    area_href = area_link.get("href", "")
    assert "dataset=conservation-area" in area_href
    assert "q=" not in area_href
    assert "latitude=" not in area_href
    assert "longitude=" not in area_href
    assert "resolved_q=" not in area_href


def test_search_entities_reuses_persisted_area_coordinates_when_query_unchanged(
    mocker,
    typologies,
    local_authorities,
    organisation_list,
    multiple_dataset_models,
):
    query_filters = QueryFilters(
        q="SW1A 1AA",
        dataset=["conservation-area"],
        latitude=51.501,
        longitude=-0.141,
    )
    _mock_search_entities_html_dependencies(
        mocker,
        query_filters,
        typologies,
        local_authorities,
        organisation_list,
        multiple_dataset_models,
    )
    find_an_area_mock = mocker.patch("application.routers.entity.find_an_area")

    request = _make_search_request(
        "q=SW1A+1AA&dataset=conservation-area&latitude=51.501&longitude=-0.141&resolved_q=SW1A+1AA"
    )
    result = search_entities(
        request=request,
        search_query="SW1A 1AA",
        query_filters=query_filters,
        extension=None,
    )

    find_an_area_mock.assert_not_called()
    assert result.context["query"]["params"]["latitude"] == 51.501
    assert result.context["query"]["params"]["longitude"] == -0.141
    assert result.context["resolved_q_value"] == "SW1A 1AA"
    assert ("resolved_q", "SW1A 1AA") not in result.context["url_query_params"]["list"]


def test_search_entities_relooks_up_area_coordinates_when_query_changed(
    mocker,
    typologies,
    local_authorities,
    organisation_list,
    multiple_dataset_models,
):
    query_filters = QueryFilters(
        q="M33 3BU",
        dataset=["conservation-area"],
        latitude=51.501,
        longitude=-0.141,
    )
    _mock_search_entities_html_dependencies(
        mocker,
        query_filters,
        typologies,
        local_authorities,
        organisation_list,
        multiple_dataset_models,
    )
    find_an_area_mock = mocker.patch(
        "application.routers.entity.find_an_area",
        return_value={
            "type": "postcode",
            "result": {"POSTCODE": "M33 3BU", "LAT": 53.4258, "LNG": -2.3248},
        },
    )

    request = _make_search_request(
        "q=M33+3BU&dataset=conservation-area&latitude=51.501&longitude=-0.141&resolved_q=SW1A+1AA"
    )
    result = search_entities(
        request=request,
        search_query="M33 3BU",
        query_filters=query_filters,
        extension=None,
    )

    find_an_area_mock.assert_called_once_with("M33 3BU")
    assert result.context["query"]["params"]["latitude"] == 53.4258
    assert result.context["query"]["params"]["longitude"] == -2.3248
    assert result.context["resolved_q_value"] == "M33 3BU"


def test_search_entities_relooks_up_area_coordinates_when_coordinates_missing(
    mocker,
    typologies,
    local_authorities,
    organisation_list,
    multiple_dataset_models,
):
    query_filters = QueryFilters(q="M33 3BU", dataset=["conservation-area"])
    _mock_search_entities_html_dependencies(
        mocker,
        query_filters,
        typologies,
        local_authorities,
        organisation_list,
        multiple_dataset_models,
    )
    find_an_area_mock = mocker.patch(
        "application.routers.entity.find_an_area",
        return_value={
            "type": "postcode",
            "result": {"POSTCODE": "M33 3BU", "LAT": 53.4258, "LNG": -2.3248},
        },
    )

    request = _make_search_request("q=M33+3BU&dataset=conservation-area")
    result = search_entities(
        request=request,
        search_query="M33 3BU",
        query_filters=query_filters,
        extension=None,
    )

    find_an_area_mock.assert_called_once_with("M33 3BU")
    assert result.context["query"]["params"]["latitude"] == 53.4258
    assert result.context["query"]["params"]["longitude"] == -2.3248
    assert result.context["resolved_q_value"] == "M33 3BU"


def test_search_entities_renders_hidden_resolved_area_inputs(
    mocker,
    typologies,
    local_authorities,
    organisation_list,
    multiple_dataset_models,
):
    query_filters = QueryFilters(
        q="SW1A 1AA",
        dataset=["conservation-area"],
        latitude=51.501,
        longitude=-0.141,
    )
    _mock_search_entities_html_dependencies(
        mocker,
        query_filters,
        typologies,
        local_authorities,
        organisation_list,
        multiple_dataset_models,
    )
    mocker.patch("application.routers.entity.find_an_area")

    request = _make_search_request(
        "q=SW1A+1AA&dataset=conservation-area&latitude=51.501&longitude=-0.141&resolved_q=SW1A+1AA"
    )
    result = search_entities(
        request=request,
        search_query="SW1A 1AA",
        query_filters=query_filters,
        extension=None,
    )
    rendered = result.template.render(result.context)
    soup = BeautifulSoup(rendered, "html.parser")
    search_form = soup.find("form", id="search-facets-form")
    assert search_form is not None
    assert search_form.find("input", {"type": "hidden", "name": "latitude"}) is not None
    assert (
        search_form.find("input", {"type": "hidden", "name": "latitude"}).get("value")
        == "51.501"
    )
    assert (
        search_form.find("input", {"type": "hidden", "name": "longitude"}) is not None
    )
    assert (
        search_form.find("input", {"type": "hidden", "name": "longitude"}).get("value")
        == "-0.141"
    )
    assert (
        search_form.find("input", {"type": "hidden", "name": "resolved_q"}).get("value")
        == "SW1A 1AA"
    )
