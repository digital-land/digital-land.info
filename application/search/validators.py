from application.data_access.dataset_queries import get_dataset_names
from application.exceptions import DatasetValueNotFound


def validate_dataset_name(dataset):
    dataset_names = get_dataset_names()
    if dataset not in dataset_names:
        raise DatasetValueNotFound(
            f"Requested dataset does not exist: {dataset}. "
            f"Valid dataset names: {','.join(dataset_names)}",
            dataset_names=dataset_names,
        )
    return dataset
