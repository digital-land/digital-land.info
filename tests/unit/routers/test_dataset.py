import pytest

from application.routers.dataset import get_datasets_by_typology

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
