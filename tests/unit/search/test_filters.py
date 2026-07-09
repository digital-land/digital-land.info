from fastapi import FastAPI
from pydantic import ValidationError

from application.routers import dataset, entity
from application.search.filters import (
    FactPathParams,
    FactQueryFilters,
    FactDatasetQueryFilters,
    QueryFilters,
)

PARAMS_NOT_REQUIRING_DESCRIPTIONS = {"extension"}


def _schema_parameter_descriptions():
    app = FastAPI()
    app.include_router(entity.router, prefix="/entity")
    app.include_router(dataset.router, prefix="/dataset")
    schema = app.openapi()
    descriptions = {}
    for methods in schema["paths"].values():
        for op in methods.values():
            for param in op.get("parameters", []):
                descriptions.setdefault(param["name"], []).append(
                    param.get("description")
                )
    return descriptions


def test_documented_parameters_have_descriptions():
    descriptions = _schema_parameter_descriptions()
    missing = [
        name
        for name, occurrences in descriptions.items()
        if name not in PARAMS_NOT_REQUIRING_DESCRIPTIONS and not all(occurrences)
    ]
    assert (
        not missing
    ), f"Parameters missing a description in the OpenAPI schema: {missing}"


# removed as typologies checking is not in the main function
# TODO use integration/acceptance test to do this
# TODO add unit tests for application.routers.entity import validate_typologies
# def test_QueryFilters_typologies_exist_invalid_typology(mocker):
#     mocker.patch(
#         "application.search.filters.get_typology_names",
#         return_value=["category"],
#     )
#     typology = ["invalid_typology"]
#     try:
#         QueryFilters(typology=typology)
#         assert False, f"invalid typology: {typology} is being labelled as valid"
#     except ValidationError:
#         assert True


def test_QueryFilters_typologies_exist_valid_typology(mocker):
    typology = ["category"]
    try:
        QueryFilters(typology=typology)
        assert True
    except ValidationError:
        assert False, f"valid typology: {typology} is being labelled as invalid"


def test_QueryFilters_invalid_entity():
    entity = [-1000]
    try:
        QueryFilters(entity=entity)
        assert False, f" invalid entity :{entity} has been labelled as valid"
    except ValidationError:
        assert True


def test_QueryFilters_valid_entity():
    entity = [11000]
    try:
        QueryFilters(entity=entity)
        assert True
    except ValidationError:
        assert False, f" valid entity :{entity} has been labelled as invalid"


# fact parameter classes
# def test_FactDatasetQueryFilters_invalid_dataset(mocker):
#     mocker.patch(
#         "application.search.validators.get_dataset_names",
#         return_value=["ancient-woodland"],
#     )
#     dataset = "invalid_name"
#     try:
#         FactDatasetQueryFilters(dataset=dataset)
#         assert False, f" invalid dataset :{dataset} has been labelled as valid"
#     except ValidationError:
#         assert True


def test_FactDatasetQueryFilters_valid_dataset(mocker):
    mocker.patch(
        "application.search.validators.get_dataset_names",
        return_value=["ancient-woodland"],
    )
    dataset = "ancient-woodland"
    try:
        FactDatasetQueryFilters(dataset=dataset)
        assert True
    except ValidationError:
        assert False, f" valid entity :{dataset} has been labelled as invalid"


def test_FactQueryFilters_integer_validator_invalid_entity_value_supplied(mocker):
    mocker.patch(
        "application.search.validators.get_dataset_names",
        return_value=["ancient-woodland"],
    )
    entity = -1000
    try:
        FactQueryFilters(dataset="ancient-woodland", entity=entity)
        assert False, f" invalid entity :{entity} has been labelled as valid"
    except ValidationError:
        assert True


def test_FactQueryFilters_integer_validator_valid_entity_value_supplied(mocker):
    mocker.patch(
        "application.search.validators.get_dataset_names",
        return_value=["ancient-woodland"],
    )
    entity = 11000
    try:
        FactQueryFilters(dataset="ancient-woodland", entity=entity)
        assert True
    except ValidationError:
        assert False, f" valid entity :{entity} has been labelled as invalid"


def test_FactPathParams_hash_sha256_regex_validator_valid_hash_supplied():
    fact = "ef355ac0a6fb494ba031daf6c675d859eb1206a5f1826b18fb538c1427fb72e6"
    try:
        FactPathParams(fact=fact)
        assert True
    except ValidationError:
        assert False, f" valid hash :{fact} has been labelled as invalid"


def test_FactPathParams_hash_sha256_regex_validator_invalid_hash_supplied():
    fact = "vrbejwiw,mbnoe bmo@@@"
    try:
        FactPathParams(fact=fact)
        assert False, f" invalid hash :{fact} has been labelled as valid"
    except ValidationError:
        assert True
