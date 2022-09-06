from pydantic.error_wrappers import ValidationError

from application.search.filters import FactPathParams


def test_hash_sha256_validator_valid_hash_supplied():
    fact = "ef355ac0a6fb494ba031daf6c675d859eb1206a5f1826b18fb538c1427fb72e6"
    try:
        FactPathParams(fact=fact)
        assert True
    except ValidationError:
        assert False, f" valid hash :{fact} has been labelled as invalid"


def test_hash_sha256_validator_invalid_hash_supplied():
    fact = "vrbejwiw,mbnoe bmo@@@"
    try:
        FactPathParams(fact=fact)
        assert False, f" invalid hash :{fact} has been labelled as valid"
    except ValidationError:
        assert True
