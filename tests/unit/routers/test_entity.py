import logging
import pytest
from application.data_access.entity_query_helpers import normalised_params
from dataclasses import asdict

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
            logging.warning(f"context:{result.context}")
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
            logging.warning(f"context:{result.context}")
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


def test_search_entities_no_entities_returned_no_query_params_html(
    mocker, typologies, local_authorities, multiple_dataset_models
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

    request = MagicMock()
    result = search_entities(
        request=request,
        query_filters=QueryFilters(),
        extension=None,
    )
    try:
        result.template.render(result.context)
        assert True
    except Exception:
        if hasattr(result, "context"):
            logging.warning(f"context:{result.context}")
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
    extension = MagicMock()
    extension.value = "json"
    result = search_entities(
        request=request,
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
    extension = MagicMock()
    extension.value = "geojson"
    result = search_entities(
        request=request,
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

    request = MagicMock()
    result = search_entities(
        request=request,
        query_filters=QueryFilters(),
        extension=None,
    )
    try:
        result.template.render(result.context)
        assert True
    except Exception:
        if hasattr(result, "context"):
            logging.warning(f"context:{result.context}")
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
    extension = MagicMock()
    extension.value = "json"
    result = search_entities(
        request=request,
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
    extension = MagicMock()
    extension.value = "geojson"
    result = search_entities(
        request=request,
        query_filters=QueryFilters(),
        extension=extension,
    )
    assert isinstance(
        result, dict
    ), f"{type(result)} is expected to be a python dictionary"
    assert "type" in result, "expecting geojson structure to have type attribute"
    assert result["type"] == "FeatureCollection"
    assert "features" in result, "expected features attribute"


def test_search_entities_exclude_field(mocker, multiple_entity_models):
    exclude_field = ["geojson"]

    mocker.patch(
        "application.routers.entity.get_entity_search",
        return_value={
            "params": normalised_params(
                asdict(QueryFilters(exclude_field=exclude_field))
            ),
            "count": len(multiple_entity_models),
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
    extension = MagicMock()
    extension.value = "json"

    result = search_entities(
        request=request,
        query_filters=QueryFilters(exclude_field=exclude_field),
        extension=extension,
    )

    assert "geojson" not in result["entities"][0]


def test_search_entities_no_exclude_field(mocker, multiple_entity_models):
    mocker.patch(
        "application.routers.entity.get_entity_search",
        return_value={
            "params": normalised_params(asdict(QueryFilters())),
            "count": len(multiple_entity_models),
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
    extension = MagicMock()
    extension.value = "json"

    result = search_entities(
        request=request,
        query_filters=QueryFilters(exclude_field=None),
        extension=extension,
    )

    for entity in result["entities"]:
        assert "geometry" in entity
