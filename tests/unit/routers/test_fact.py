import logging

from fastapi.exceptions import HTTPException

from unittest.mock import MagicMock
from pydantic import BaseModel
import pytest
from application.routers.fact import _convert_model_to_dict, get_fact, search_facts
from application.core.models import DatasetFieldModel, EntityModel, FactModel
from application.search.filters import FactDatasetQueryFilters, FactQueryFilters


def test__convert_model_to_dict_single_model():
    model = BaseModel()
    result = _convert_model_to_dict(model)
    assert result == {}


def test__convert_model_to_dict_list_of_model():
    models = [BaseModel(), BaseModel(), BaseModel()]
    result = _convert_model_to_dict(models)
    assert result == [{}, {}, {}]


# create fixture that represents the fact models returned by get_fact_query
@pytest.fixture
def query_params(mocker):
    # need to mock validation so dataset isn't queried
    mocker.patch(
        "application.search.filters.get_dataset_names",
        return_value=["ancient-woodland"],
    )
    output = FactDatasetQueryFilters(dataset="ancient-woodland")
    return output


def test_get_fact_no_fact_returned_for_html(mocker, query_params):
    mocker.patch("application.routers.fact.get_fact_query", return_value=None)
    request = MagicMock()
    try:
        get_fact(
            request=request,
            fact="180b185fbe277e7ae6d0da63b57eb46549d21fd6424e9890c4cd73f9490dde93",
            query_filters=query_params,
            extension=None,
        )
        assert False, "Expected HTTPException to be raised"
    except HTTPException:
        assert True


def test_get_fact_no_facts_returned_for_json(mocker, query_params):
    mocker.patch("application.routers.fact.get_fact_query", return_value=None)
    request = MagicMock()
    extension = MagicMock()
    extension.value = "json"
    try:
        get_fact(
            request=request,
            fact="180b185fbe277e7ae6d0da63b57eb46549d21fd6424e9890c4cd73f9490dde93",
            query_filters=query_params,
            extension=extension,
        )
        assert False, "Expected HTTPException to be raised"
    except HTTPException:
        assert True


@pytest.fixture
def single_fact_model():
    output = FactModel(
        fact="180b185fbe277e7ae6d0da63b57eb46549d21fd6424e9890c4cd73f9490dde93",
        entity=110000000,
        reference_entity=None,
        field="name",
        value="Abbotswood Shaw",
        entity_name="Abbotswood Shaw",
        entity_prefix="ancient-woodland",
        entity_reference="1481207",
        earliest_entry_date="2021-05-26",
        latest_entry_date="2022-03-23",
        latest_resource="80709f042768e421a82f4aaa523f34b837e77af71b4c8afcd7f4f05938e9e98b",
        resources=(
            "["
            '{"resource":"80709f042768e421a82f4aaa523f34b837e77af71b4c8afcd7f4f05938e9e98b","entry_date":"2022-03-23"},'
            '{"resource":"87a4898736b177e886dc0722c3403b12989a563c272a6c55a70be1e4a307f94c","entry_date":"2021-12-01"},'
            '{"resource":"89632d544d34d2745cbfc2ec034fbdae2a74c235ea07acd67d920c4cebddc3c0","entry_date":"2021-05-26"}'
            "]"
        ),
    )
    return output


def test_get_fact_fact_returned_for_html(mocker, single_fact_model, query_params):
    mocker.patch(
        "application.routers.fact.get_fact_query", return_value=single_fact_model
    )
    request = MagicMock()
    result = get_fact(
        request=request,
        fact="180b185fbe277e7ae6d0da63b57eb46549d21fd6424e9890c4cd73f9490dde93",
        query_filters=query_params,
        extension=None,
    )
    # check response code and response type are correct
    assert (
        result.status_code == 200
    ), f"result status code should be 200 not {result.status_code}"
    try:
        result.template.render(result.context)
    except Exception:
        logging.warning(f"context:{result.context}")
        assert False, "template unable to render, missing variable(s) from context"


def test_get_fact_fact_returned_for_json(mocker, single_fact_model, query_params):
    mocker.patch(
        "application.routers.fact.get_fact_query", return_value=single_fact_model
    )
    request = MagicMock()
    extension = MagicMock()
    extension.value = "json"
    result = get_fact(
        request=request,
        fact="180b185fbe277e7ae6d0da63b57eb46549d21fd6424e9890c4cd73f9490dde93",
        query_filters=query_params,
        extension=extension,
    )
    assert isinstance(
        result, dict
    ), f"{type(result)} is expected to be a python dictionary"


@pytest.fixture
def multiple_fact_models(mocker):
    model_1 = FactModel(
        fact="180b185fbe277e7ae6d0da63b57eb46549d21fd6424e9890c4cd73f9490dde93",
        entity=110000000,
        reference_entity=None,
        field="name",
        value="Abbotswood Shaw",
        entity_name="Abbotswood Shaw",
        entity_prefix="ancient-woodland",
        entity_reference="1481207",
        earliest_entry_date="2021-05-26",
        latest_entry_date="2022-03-23",
        latest_resource="80709f042768e421a82f4aaa523f34b837e77af71b4c8afcd7f4f05938e9e98b",
        resources=(
            "["
            '{"resource":"80709f042768e421a82f4aaa523f34b837e77af71b4c8afcd7f4f05938e9e98b","entry_date":"2022-03-23"},'
            '{"resource":"87a4898736b177e886dc0722c3403b12989a563c272a6c55a70be1e4a307f94c","entry_date":"2021-12-01"},'
            '{"resource":"89632d544d34d2745cbfc2ec034fbdae2a74c235ea07acd67d920c4cebddc3c0","entry_date":"2021-05-26"}'
            "]"
        ),
    )

    model_2 = FactModel(
        fact="180b185fbe277e7ae6d0da63b57eb46549d21fd6424e9890c4cd73f9490dde93",
        entity=110000000,
        reference_entity=None,
        field="reference",
        value="1481207",
        entity_name="Abbotswood Shaw",
        entity_prefix="ancient-woodland",
        entity_reference="1481207",
        earliest_entry_date="2021-05-26",
        latest_entry_date="2022-03-23",
        latest_resource="80709f042768e421a82f4aaa523f34b837e77af71b4c8afcd7f4f05938e9e98b",
        resources=(
            "["
            '{"resource":"80709f042768e421a82f4aaa523f34b837e77af71b4c8afcd7f4f05938e9e98b","entry_date":"2022-03-23"},'
            '{"resource":"87a4898736b177e886dc0722c3403b12989a563c272a6c55a70be1e4a307f94c","entry_date":"2021-12-01"},'
            '{"resource":"89632d544d34d2745cbfc2ec034fbdae2a74c235ea07acd67d920c4cebddc3c0","entry_date":"2021-05-26"}'
            "]"
        ),
    )
    return [model_1, model_2]


@pytest.fixture
def multiple_dataset_field_models():
    output = [
        DatasetFieldModel(field="geometry"),
        DatasetFieldModel(field="name"),
        DatasetFieldModel(field="reference"),
    ]
    return output


@pytest.fixture
def single_entity_model():
    output = EntityModel(
        entity=11000000,
        entry_date="2022-03-23",
        name="Abbotswood Shaw",
        reference="1481207",
        dataset="ancient-woodland",
        prefix="ancient-woodland",
    )
    return output


@pytest.fixture
def search_query_parameters(mocker):
    # need to mock validation so dataset isn't queried
    def return_value(cls, dataset: str):
        return dataset

    mocker.patch(
        "application.search.filters.get_dataset_names",
        return_value=["ancient-woodland"],
    )
    output = FactQueryFilters(
        dataset="ancient-woodland", entity=110000000, field=["name", "reference"]
    )
    return output


def test_search_facts_no_facts_returned_html(
    mocker, search_query_parameters, multiple_dataset_field_models, single_entity_model
):
    mocker.patch("application.routers.fact.get_search_facts_query", return_value=[])
    mocker.patch(
        "application.routers.fact.get_dataset_fields",
        return_value=multiple_dataset_field_models,
    )
    mocker.patch(
        "application.routers.fact.get_entity_query",
        return_value=(single_entity_model, None, None),
    )
    request = MagicMock()
    result = search_facts(
        request=request,
        query_filters=search_query_parameters,
        extension=None,
    )
    # check response code and response type are correct
    assert (
        result.status_code == 200
    ), f"result status code should be 200 not {result.status_code}"
    try:
        result.template.render(result.context)
    except Exception:
        logging.warning(f"context:{result.context}")
        assert False, "template unable to render, missing variable(s) from context"


def test_search_facts_no_facts_returned_json(
    mocker, search_query_parameters, multiple_dataset_field_models, single_entity_model
):
    mocker.patch("application.routers.fact.get_search_facts_query", return_value=[])
    mocker.patch(
        "application.routers.fact.get_dataset_fields",
        return_value=multiple_dataset_field_models,
    )
    mocker.patch(
        "application.routers.fact.get_entity_query",
        return_value=(single_entity_model, None, None),
    )

    request = MagicMock()
    extension = MagicMock()
    extension.value = "json"
    result = search_facts(
        request=request,
        query_filters=search_query_parameters,
        extension=extension,
    )
    # check response code and response type are correct
    assert isinstance(result, list), f"{type(result)} is expected to be a python list"


def test_search_facts_multiple_facts_returned_html(
    mocker, multiple_fact_models, search_query_parameters, multiple_dataset_field_models
):
    mocker.patch(
        "application.routers.fact.get_search_facts_query",
        return_value=multiple_fact_models,
    )
    mocker.patch(
        "application.routers.fact.get_dataset_fields",
        return_value=multiple_dataset_field_models,
    )
    get_entity_query_mock = MagicMock()
    get_entity_query_mock.return_value = (None, None, None)
    mocker.patch("application.routers.fact.get_entity_query", get_entity_query_mock)
    request = MagicMock()
    result = search_facts(
        request=request,
        query_filters=search_query_parameters,
        extension=None,
    )
    # check response code and response type are correct
    assert (
        result.status_code == 200
    ), f"result status code should be 200 not {result.status_code}"
    get_entity_query_mock.assert_not_called()
    try:
        result.template.render(result.context)
    except Exception:
        logging.warning(f"context:{result.context}")
        assert False, "template unable to render, missing variable(s) from context"


def test_search_facts_multiple_facts_returned_json(
    mocker, multiple_fact_models, search_query_parameters, multiple_dataset_field_models
):
    mocker.patch("application.routers.fact.get_search_facts_query", return_value=[])
    mocker.patch(
        "application.routers.fact.get_dataset_fields",
        return_value=multiple_dataset_field_models,
    )
    get_entity_query_mock = MagicMock()
    get_entity_query_mock.return_value = (None, None, None)
    mocker.patch("application.routers.fact.get_entity_query", get_entity_query_mock)
    request = MagicMock()
    extension = MagicMock()
    extension.value = "json"
    result = search_facts(
        request=request,
        query_filters=search_query_parameters,
        extension=extension,
    )
    # check get_entity_query isn;t being called
    get_entity_query_mock.assert_not_called()
    assert isinstance(result, list), f"{type(result)} is expected to be a python list"
