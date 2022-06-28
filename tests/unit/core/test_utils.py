from application.core.utils import entity_attribute_sort_key, make_pagination_query_str


def test_entity_attribute_sort_key_only_excepts_string():
    integer = 10
    try:
        entity_attribute_sort_key(integer)
        assert False
    except ValueError:
        assert True


def test_make_pagination_query_str_preserves_repeated_key_params():
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
