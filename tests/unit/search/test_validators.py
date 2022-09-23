import pytest

from application.search.validators import (
    validate_dataset_name,
    validate_day_integer,
    validate_month_integer,
    validate_year_integer,
    validate_curies,
)

from application.exceptions import DigitalLandValidationError, DatasetValueNotFound


def test_validate_dataset_name_invalid_value_provided(mocker):
    mocker.patch(
        "application.search.validators.get_dataset_names",
        return_value=["ancient-woodland"],
    )
    dataset = "invalid_dataset"
    try:
        validate_dataset_name(dataset)
        assert False, f" invalid entity :{dataset} has been labelled as valid"
    except DatasetValueNotFound:
        assert True


def test_validate_dataset_name_valid_value_provided(mocker):
    mocker.patch(
        "application.search.validators.get_dataset_names",
        return_value=["ancient-woodland"],
    )
    dataset = "ancient-woodland"
    try:
        validate_dataset_name(dataset)
        assert True
    except DigitalLandValidationError:
        assert False, f" valid entity :{dataset} has been labelled as invalid"


def test_validate_day_integer_invalid_value_provided():
    invalid_integer = 48
    try:
        validate_day_integer(invalid_integer)
        assert (
            False
        ), f"invalid integer value {invalid_integer} is being labelled as valid"
    except DigitalLandValidationError:
        assert True


def test_validate_day_integer_valid_value_provided():
    valid_integer = 16
    try:
        validate_day_integer(valid_integer)
        assert True
    except DigitalLandValidationError:
        assert (
            False
        ), f"valid integer value {valid_integer} is being labelled as invalid"


def test_validate_month_integer_invalid_value_provided():
    invalid_integer = 48
    try:
        validate_month_integer(invalid_integer)
        assert (
            False
        ), f"invalid integer value {invalid_integer} is being labelled as valid"
    except DigitalLandValidationError:
        assert True


def test_validate_month_integer_valid_value_provided():
    valid_integer = 10
    try:
        validate_month_integer(valid_integer)
        assert True
    except DigitalLandValidationError:
        assert (
            False
        ), f"valid integer value {valid_integer} is being labelled as invalid"


def test_validate_year_integer_invalid_value_provided():
    invalid_integer = -1
    try:
        validate_year_integer(invalid_integer)
        assert (
            False
        ), f"invalid integer value {invalid_integer} is being labelled as valid"
    except DigitalLandValidationError:
        assert True


def test_validate_year_integer_valid_value_provided():
    valid_integer = 16
    try:
        validate_year_integer(valid_integer)
        assert True
    except DigitalLandValidationError:
        assert (
            False
        ), f"valid integer value {valid_integer} is being labelled as invalid"


valid_curies = [
    "prefix:reference",
    "PREFIX:REFERENCE",
    "01234:56789",
    "prefix01234:reference56789",
    "01234prefix:56789reference",
    "a:b",
    "1:2",
]


@pytest.mark.parametrize("curie", valid_curies)
def test_validate_valid_curie(curie):
    try:
        validate_curies([curie])
        assert True
    except DigitalLandValidationError:
        assert False, f"valid curie value {curie} should not be rejected as invalid"


invalid_curies = [
    "",
    "prefix",
    "prefix:",
    ":reference",
    "prefix::reference",
    "prefix : reference",
    " prefix:reference",
    "prefix:reference ",
    "just-a-to-z-and-numbers-allowed",
    "null",
    "and no : spaces allowed",
    "eval(print('malicious code'))",
    "@:&",
]


@pytest.mark.parametrize("curie", invalid_curies)
def test_validate_invalid_curie(curie):

    with pytest.raises(DigitalLandValidationError):
        validate_curies([curie])


def test_validate_curies_rejects_all_if_any_invalid():
    curies = [
        "prefix:reference",
        "01234:56789",
        "this is an invalid:curie",
    ]
    with pytest.raises(DigitalLandValidationError):
        validate_curies(curies)
