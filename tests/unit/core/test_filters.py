from application.core.filters import (
    _remove_value_from_list,
    remove_param_from_param_dict,
    remove_values_from_param_dict,
    make_url_param_str,
)


def test__remove_value_from_list_element_to_exclude():
    input_list = ["value_1", "value_2"]
    exclude_value = "value_2"
    expected = ["value_1"]

    result = _remove_value_from_list(input_list, exclude_value)
    assert result == expected


def test__remove_value_from_list_list_to_exclude():
    input_list = ["value_1", "value_2", "value_3"]
    exclude_value_list = ["value_1", "value_3"]
    expected = ["value_2"]

    result = _remove_value_from_list(input_list, exclude_value_list)
    assert result == expected


def test_remove_param_from_param_dict_element_param():
    input_param_dict = {"field": ["point", "typology"], "dataset": "ancient-woodland"}
    exclude_param = "field"
    expected = {"dataset": "ancient-woodland"}
    result = remove_param_from_param_dict(input_param_dict, exclude_param)
    assert result == expected


def test_remove_param_from_param_dict_list_of_param():
    input_param_dict = {
        "field": ["point", "typology"],
        "dataset": "ancient-woodland",
        "test": "test_value_1",
    }
    exclude_param = ["field", "test"]
    expected = {"dataset": "ancient-woodland"}
    result = remove_param_from_param_dict(input_param_dict, exclude_param)
    assert result == expected


def test_remove_values_from_param_dict_elements_provided():
    input_param_dict = {
        "field": ["point", "typology"],
        "dataset": "ancient-woodland",
        "test": "test_value_1",
    }
    exclude_values = {"field": "point"}
    expected = {
        "field": ["typology"],
        "dataset": "ancient-woodland",
        "test": "test_value_1",
    }
    result = remove_values_from_param_dict(input_param_dict, exclude_values)
    assert result == expected


def test_remove_values_from_param_dict_lists_provided():
    input_param_dict = {
        "field": ["point", "typology"],
        "dataset": "ancient-woodland",
        "test": ["test_value_1", "test_value_2", "test_value_3"],
    }
    exclude_values = {"field": ["point"], "test": ["test_value_1", "test_value_2"]}
    expected = {
        "field": ["typology"],
        "dataset": "ancient-woodland",
        "test": ["test_value_3"],
    }
    result = remove_values_from_param_dict(input_param_dict, exclude_values)
    assert result == expected


def test_make_url_param_str_all_arguements():
    input_param_dict = {
        "field": ["point", "typology"],
        "dataset": "ancient-woodland",
        "test": ["test_value_1", "test_value_2", "test_value_3"],
    }
    exclude_params = "dataset"
    exclude_values = {"field": "point"}
    expected = "field=typology&test=test_value_1&test=test_value_2&test=test_value_3"
    result = make_url_param_str(input_param_dict, exclude_values, exclude_params)
    assert result == expected
