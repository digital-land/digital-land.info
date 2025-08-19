from unittest.mock import MagicMock
from application.search.filters import QueryFilters
import pytest

from application.routers.dataset import get_datasets_by_typology, list_datasets

from application.core.models import DatasetModel


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
        (QueryFilters(), 2, True),  # No filters
        (
            QueryFilters(dataset=["ancient-woodland-status"], field=["name"]),
            1,
            True,
        ),  # Filter by dataset
        (
            QueryFilters(
                dataset=["ancient-woodland-status"],
                field=["name"],
                include_typologies=False,
            ),
            1,
            False,
        ),  # Exclude typologies
    ],
)
def test_list_datasets(
    mocker, multiple_dataset_models, query_filters, expected_count, expect_typologies
):
    mocker.patch(
        "application.routers.dataset.get_all_datasets",
        return_value=multiple_dataset_models,
    )
    mocker.patch(
        "application.routers.dataset.get_entity_count",
        return_value=[(ds.dataset, 10) for ds in multiple_dataset_models],
    )
    mocker.patch(
        "application.routers.dataset.get_datasets_by_typology",
        return_value={
            "geography": [multiple_dataset_models[0]],
            "category": [multiple_dataset_models[1]],
        },
    )

    mock_get_session = mocker.patch(
        "application.routers.dataset.get_session", return_value=MagicMock()
    )

    result = list_datasets(
        request=MagicMock(),
        extension=MagicMock(value="json"),
        query_filters=query_filters,
        session=mock_get_session,
        redis=None,
    )
    assert len(result["datasets"]) == expected_count

    if query_filters and query_filters.field:
        assert "name" in result["datasets"][0]

    if expect_typologies:
        assert result["typologies"] != ""
    else:
        assert result["typologies"] == ""
