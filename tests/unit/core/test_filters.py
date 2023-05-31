from application.core.filters import (
    _remove_value_from_list,
    remove_param_from_param_dict,
    remove_values_from_param_dict,
    make_url_param_str,
    cacheBust,
    appendUriParam,
    hash_file,
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


def test_cacheBust_no_params():
    input_uri = "static/javascripts/application.js"
    result = cacheBust(input_uri)
    sections = result.split("?")
    assert input_uri == sections[0]

    hash = sections[1].split("=")[1]
    assert len(hash) == 40


def test_cacheBust_params():
    input_uri = "static/javascripts/application.js?fakeParam=myFakeParam"
    result = cacheBust(input_uri)
    sections = result.split("?")
    assert "static/javascripts/application.js" == sections[0]

    params = sections[1].split("&")
    assert params[0] == "fakeParam=myFakeParam"

    hash = params[1].split("=")[1]
    assert len(hash) == 40


def test_appendUriParam():
    uri = "static/javascript/myCookScript.js"
    param = {"key": "value"}
    result = appendUriParam(uri, param)
    assert result == "static/javascript/myCookScript.js?key=value"

    uri = "static/javascript/myCookScript.js?key=value"
    param = {"differentKey": "differentValue"}
    result = appendUriParam(uri, param)
    assert (
        result
        == "static/javascript/myCookScript.js?key=value&differentKey=differentValue"
    )


def test_hash_file():
    result = hash_file("static/javascripts/application.js")
    print(result)
    assert len(result) == 40


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
