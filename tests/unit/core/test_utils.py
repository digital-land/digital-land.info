from application.core.utils import entity_attribute_sort_key, make_pagination_query_str


def test_entity_attribute_sort_key_only_excepts_string():
    integer = 10
    try:
        entity_attribute_sort_key(integer)
        assert False
    except ValueError:
        assert True


def test_make_pagination_query_str_excepts_normalised_params():
    normalised_param = {
        "dataset": "ancient-woodland",
        "geometry_curie": [
            "statistical-geography:E07000223",
            "statistical-geography:E07000026",
        ],
    }
    limit = 10
    offset = 0

    expected = (
        "?"
        "dataset=ancient-woodland"
        "&geometry_curie=statistical-geography:E07000223"
        "&geometry_curie=statistical-geography:E07000026"
        "&limit=10"
    )
    result = make_pagination_query_str(normalised_param, limit, offset)
    assert expected == result
