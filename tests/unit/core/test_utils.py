import pytest

from application.core.utils import (
    entity_attribute_sort_key,
    map_entity_quality_to_description,
    make_pagination_query_str,
)


def test_entity_attribute_sort_key_only_excepts_string():
    integer = 10
    try:
        entity_attribute_sort_key(integer)
        assert False
    except ValueError:
        assert True


def test_make_pagination_query_str_preserves_repeated_key_params_when_adding_limit_or_offset():
    query_string_several_datasets = (
        "dataset=ancient-woodland&dataset=battlefield&dataset=conservation-area"
    )

    limit = 10
    offset = 0

    expected = f"{query_string_several_datasets}&limit={limit}"
    result = make_pagination_query_str(query_string_several_datasets, limit, offset)

    assert expected == result

    limit = 10
    offset = 20

    expected = f"{query_string_several_datasets}&limit={limit}&offset={offset}"
    result = make_pagination_query_str(query_string_several_datasets, limit, offset)

    assert expected == result


quality_test_data = [
    (
        {"quality": "authoritative", "name": "Brownfield site"},
        "Authoritative: We have some data from the authoritative source",
    ),
    (
        {"quality": "some", "name": "Historical monument"},
        "Some: We have some data from an alternative source",
    ),
    (
        {"quality": "trustworthy", "name": "Historic England"},
        "Trustworthy: We have authorititive data linked to material information",
    ),
    (
        {"quality": "usable", "name": "Green space"},
        "Usable: We have data from the authoritative source",
    ),
]


@pytest.mark.parametrize("entity_dict, expected", quality_test_data)
def test_map_entity_quality_to_description_successfully(entity_dict, expected):
    """Test mapping the quality field value to the right description."""
    result = map_entity_quality_to_description(entity_dict)
    assert result["quality"] == expected


def test_map_entity_quality_to_description_with_empty_quality():
    """Test function when the quality value is `None`."""
    entity_dict = {"quality": None, "name": "Test Entity"}
    result = map_entity_quality_to_description(entity_dict)
    assert result["quality"] == "We have no data"


def test_map_entity_quality_to_description_with_unknown_quality():
    """Test mapping fails, falls back gracefully."""
    entity_dict = {"quality": "special quality", "name": "Test Entity"}
    result = map_entity_quality_to_description(entity_dict)

    # Should title case the quality even if description not found
    assert result["quality"] == "Special quality"
