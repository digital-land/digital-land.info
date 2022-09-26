import re
from typing import Optional, List

from application.data_access.dataset_queries import get_dataset_names
from application.exceptions import DatasetValueNotFound, DigitalLandValidationError


def validate_dataset_name(dataset):
    dataset_names = get_dataset_names()
    if dataset not in dataset_names:
        raise DatasetValueNotFound(
            f"Requested dataset does not exist: {dataset}. "
            f"Valid dataset names: {','.join(dataset_names)}",
            dataset_names=dataset_names,
        )
    return dataset


def validate_day_integer(integer):
    if integer is None or 1 <= integer <= 31:
        return integer
    else:
        raise DigitalLandValidationError(
            "ensure this value is greater than or equal to 1 and less than or equal to 31"
        )


def validate_month_integer(integer):
    if integer is None or 1 <= integer <= 12:
        return integer
    else:
        raise DigitalLandValidationError(
            "ensure this value is greater than or equal to 1 and less than or equal to 12"
        )


def validate_year_integer(integer):
    if integer is None or 1 <= integer:
        return integer
    else:
        raise DigitalLandValidationError(
            "ensure this value is greater than or equal to 1"
        )


def validate_curies(curies: Optional[List[str]]):
    if not curies:
        return curies
    for curie in curies:
        parts = curie.split(":")
        if len(parts) != 2:
            raise DigitalLandValidationError("curie must be in form 'prefix:reference'")
        else:
            prefix, reference = parts
            prefix_match = re.match(r"(?i)^[a-zA-Z_\d]+[a-zA-Z_\-\d]+$", prefix)
            reference_match = re.match(r"^\S+.*\S$", reference)
            if prefix_match is None or reference_match is None:
                raise DigitalLandValidationError(
                    "curie must be in form 'prefix:reference'"
                )
            # TODO - references a bit too lax, should they be more restricted?
    return curies
