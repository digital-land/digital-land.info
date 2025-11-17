from application.core.models import DatasetModel
from application.data_access.digital_land_queries import get_dataset_filter_fields


def test_get_dataset_filter_fields():
    dataset = DatasetModel(
        collection="ancient-woodland",
        dataset="ancient-woodland-status",
        name="Ancient woodland status",
        plural="Ancient woodlands status",
        typology="category",
    )

    result = get_dataset_filter_fields(dataset, ["name", "dataset"])

    assert "name" in result
    assert "dataset" in result
    assert result["name"] == "Ancient woodland status"
