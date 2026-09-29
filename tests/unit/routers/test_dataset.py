from unittest.mock import MagicMock
from application.core.utils import to_snake
from application.search.filters import DatasetQueryFilters
import pytest

from application.routers.dataset import (
    get_dataset,
    get_datasets_by_typology,
    list_datasets,
)

from application.core.models import DatasetModel


@pytest.mark.parametrize(
    "counts, expected", [([("ancient-woodland", 10)], 10), ([], 0)]
)
def test_get_dataset_count(mocker, multiple_dataset_models, counts, expected):
    session = MagicMock()
    mocker.patch(
        "application.routers.dataset.get_dataset_query",
        return_value=multiple_dataset_models[0],
    )
    count_query = mocker.patch(
        "application.routers.dataset.get_entity_count", return_value=counts
    )

    result = get_dataset(
        request=MagicMock(),
        dataset="ancient-woodland",
        settings=MagicMock(),
        extension=MagicMock(value="json"),
        session=session,
    )

    count_query.assert_called_once_with(session, datasets=["ancient-woodland"])
    assert result.entity_count == expected


@pytest.fixture
def multiple_dataset_models():
    model_1 = DatasetModel(
        collection="ancient-woodland",
        dataset="ancient-woodland",
        name="Ancient woodland",
        plural="Ancient woodlands",
        typology="geography",
    )
    model_2 = DatasetModel(
        collection="ancient-woodland",
        dataset="ancient-woodland-status",
        name="Ancient woodland status",
        plural="Ancient woodlands status",
        typology="category",
    )
    return [model_1, model_2]


@pytest.fixture(autouse=True)
def mock_dataset_names(mocker, multiple_dataset_models):
    mocker.patch(
        "application.search.validators.get_dataset_names",
        return_value=[ds.dataset for ds in multiple_dataset_models],
    )


def test_get_datasets_by_typology_both_have_greater_than_zero_entity(
    multiple_dataset_models,
):
    multiple_dataset_models[0].entity_count = 4
    multiple_dataset_models[1].entity_count = 8

    result = get_datasets_by_typology(multiple_dataset_models)
    for typology in ["geography", "category"]:
        assert typology in result.keys(), f"{typology} missing from result"


@pytest.mark.parametrize(
    "query_filters, expected_count, expect_typologies",
    [
        (DatasetQueryFilters(), 2, True),  # No filters
        (
            DatasetQueryFilters(dataset=["ancient-woodland-status"], field=["name"]),
            1,
            True,
        ),  # Filter by dataset
        (
            DatasetQueryFilters(
                dataset=["ancient-woodland-status"],
                field=["name"],
                include_typologies=False,
            ),
            1,
            False,
        ),  # Exclude typologies
        (
            DatasetQueryFilters(
                dataset=["ancient-woodland-status"],
                field=["name"],
                exclude_field=["plural, collection"],
            ),
            1,
            True,
        ),
    ],
)
def test_list_datasets(
    mocker, multiple_dataset_models, query_filters, expected_count, expect_typologies
):
    mocker.patch(
        "application.routers.dataset.get_all_datasets",
        return_value=multiple_dataset_models,
    )
    mock_entity_count = mocker.patch(
        "application.routers.dataset.get_entity_count",
        return_value=[(ds.dataset, 10) for ds in multiple_dataset_models],
    )
    mocker.patch(
        "application.routers.dataset.get_datasets_by_typology",
        return_value={
            "geography": {"dataset": [multiple_dataset_models[0]]},
            "category": {"dataset": [multiple_dataset_models[1]]},
        },
    )

    mock_session = MagicMock()

    result = list_datasets(
        request=MagicMock(),
        extension=MagicMock(value="json"),
        query_filters=query_filters,
        session=mock_session,
        redis=None,
    )
    assert len(result["datasets"]) == expected_count
    mock_entity_count.assert_called_once_with(mock_session)

    if query_filters and query_filters.field:
        assert "name" in result["datasets"][0]

    if expect_typologies:
        assert "typologies" in result
    else:
        assert "typologies" not in result

    if query_filters and query_filters.exclude_field:
        excluded = {
            to_snake(part.strip())
            for item in query_filters.exclude_field
            for part in item.split(",")
            if part.strip()
        }
        for field in excluded:
            assert field not in result["datasets"][0]


@pytest.mark.parametrize(
    "excluded",
    [
        ["entity-count"],
        ["entity_count"],
        ["name, entity-count"],
        ["name", " entity-count "],
    ],
)
def test_get_dataset_skips_excluded_entity_count(
    mocker, multiple_dataset_models, excluded
):
    dataset = multiple_dataset_models[0]
    dataset.entity_count = 99
    mocker.patch("application.routers.dataset.get_dataset_query", return_value=dataset)
    count = mocker.patch("application.routers.dataset.get_entity_count")
    result = get_dataset(
        request=MagicMock(),
        dataset=dataset.dataset,
        settings=MagicMock(),
        extension=MagicMock(value="json"),
        session=MagicMock(),
        exclude_field=excluded,
    )
    count.assert_not_called()
    assert result["dataset"] == dataset.dataset
    assert "entity-count" not in result
    assert "entity_count" not in result
    assert dataset.entity_count == 99
    if "name" in ",".join(excluded):
        assert "name" not in result


def test_get_dataset_other_exclusions_keep_count(mocker, multiple_dataset_models):
    mocker.patch(
        "application.routers.dataset.get_dataset_query",
        return_value=multiple_dataset_models[0],
    )
    count = mocker.patch(
        "application.routers.dataset.get_entity_count",
        return_value=[("ancient-woodland", 10)],
    )
    session = MagicMock()
    result = get_dataset(
        request=MagicMock(),
        dataset="ancient-woodland",
        settings=MagicMock(),
        extension=MagicMock(value="json"),
        session=session,
        exclude_field=["name"],
    )
    count.assert_called_once_with(session, datasets=["ancient-woodland"])
    assert "name" not in result
    assert result["entity-count"] == 10


def test_get_dataset_html_keeps_count(mocker, multiple_dataset_models):
    mocker.patch(
        "application.routers.dataset.get_dataset_query",
        return_value=multiple_dataset_models[0],
    )
    count = mocker.patch(
        "application.routers.dataset.get_entity_count", return_value=[]
    )
    mocker.patch("application.routers.dataset.get_latest_resource", return_value=None)
    mocker.patch(
        "application.routers.dataset.get_dataset_coverage_status", return_value=None
    )
    mocker.patch(
        "application.routers.dataset.get_providers_for_dataset", return_value=[]
    )
    render = mocker.patch("application.routers.dataset.templates.TemplateResponse")
    session = MagicMock()
    get_dataset(
        request=MagicMock(),
        dataset="ancient-woodland",
        settings=MagicMock(),
        session=session,
        exclude_field=["entity-count"],
    )
    count.assert_called_once_with(session, datasets=["ancient-woodland"])
    assert render.call_args.args[2]["entity_count"] == 0


def test_get_dataset_exclusion_preserves_not_found(mocker):
    from fastapi import HTTPException

    mocker.patch("application.routers.dataset.get_dataset_query", return_value=None)
    count = mocker.patch("application.routers.dataset.get_entity_count")
    with pytest.raises(HTTPException) as error:
        get_dataset(
            request=MagicMock(),
            dataset="missing",
            settings=MagicMock(),
            extension=MagicMock(value="json"),
            session=MagicMock(),
            exclude_field=["entity-count"],
        )
    assert error.value.status_code == 404
    count.assert_not_called()


def test_get_dataset_json_exclude_field_query_parameter(
    mocker, multiple_dataset_models
):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from application.routers.dataset import router, get_session, get_settings

    app = FastAPI()
    app.include_router(router, prefix="/dataset")
    app.dependency_overrides[get_session] = lambda: MagicMock()
    app.dependency_overrides[get_settings] = lambda: MagicMock()
    mocker.patch(
        "application.routers.dataset.get_dataset_query",
        return_value=multiple_dataset_models[0],
    )
    count = mocker.patch("application.routers.dataset.get_entity_count")
    response = TestClient(app).get(
        "/dataset/ancient-woodland.json?exclude_field=entity-count&exclude_field=name"
    )
    assert response.status_code == 200
    assert response.json()["dataset"] == "ancient-woodland"
    assert "entity-count" not in response.json()
    assert "name" not in response.json()
    count.assert_not_called()
