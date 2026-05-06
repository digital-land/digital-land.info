from datetime import datetime
from dateutil.relativedelta import relativedelta

from application.core.filters import (
    _remove_value_from_list,
    remove_param_from_param_dict,
    remove_values_from_param_dict,
    make_url_param_str,
    make_param_str_filter,
    cacheBust,
    append_uri_param,
    hash_file,
    is_past_date,
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
    input_uri = "static/javascripts/MapController.js"
    result = cacheBust(input_uri)
    sections = result.split("?")
    assert input_uri == sections[0]

    hash = sections[1].split("=")[1]
    assert len(hash) == 40


def test_cacheBust_params():
    input_uri = "static/javascripts/MapController.js?fakeParam=myFakeParam"
    result = cacheBust(input_uri)
    sections = result.split("?")
    assert "static/javascripts/MapController.js" == sections[0]

    params = sections[1].split("&")
    assert params[0] == "fakeParam=myFakeParam"

    hash = params[1].split("=")[1]
    assert len(hash) == 40


def test_append_uri_param():
    uri = "static/javascript/myCookScript.js"
    param = {"key": "value"}
    result = append_uri_param(uri, param)
    assert result == "static/javascript/myCookScript.js?key=value"

    uri = "static/javascript/myCookScript.js?key=value"
    param = {"differentKey": "differentValue"}
    result = append_uri_param(uri, param)
    assert (
        result
        == "static/javascript/myCookScript.js?key=value&differentKey=differentValue"
    )


def test_hash_file():
    result = hash_file("static/javascripts/MapController.js")
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


def test_make_param_str_filter_url_encoding():
    """Tests that special characters are properly URL encoded."""
    params = [
        ("dataset", "planning-application"),
        ("entity", "123;456"),
        ("field", "test&value"),
    ]
    exclude_value = "nonexistent"
    exclude_param = "nonexistent"

    result = make_param_str_filter(exclude_value, exclude_param, params)

    assert "dataset=planning-application" in result
    assert "entity=123%3B456" in result  # ; becomes %3B
    assert "field=test%26value" in result  # & becomes %26


def test_make_param_str_filter_with_empty_params():
    """Tests passing empty parameter list to `make_param_str_filter` returns empty string."""
    params = []
    exclude_value = "test"
    exclude_param = "test"

    result = make_param_str_filter(exclude_value, exclude_param, params)
    assert result == ""


def test_make_param_str_filter_no_exclusions():
    """Tests no parameters match the exclusion criteria."""
    params = [("dataset", "test"), ("entity", "123")]
    exclude_value = "nonexistent"
    exclude_param = "nonexistent"

    result = make_param_str_filter(exclude_value, exclude_param, params)
    assert "dataset=test" in result
    assert "entity=123" in result


def test_make_param_str_filter_prevents_malformed_urls():
    """Tests that make_param_str_filter prevents creation of malformed URLs like &amp;entity=."""
    params = [("dataset", "planning"), ("entity", "115;00041"), ("field", "entry-date")]
    exclude_value = "nonexistent"
    exclude_param = "nonexistent"

    result = make_param_str_filter(exclude_value, exclude_param, params)

    assert "115%3B00041" in result  # Semicolon is enconded
    assert ";" not in result  # Raw semicoln does not leak through
    assert "amp;" not in result  # No amp; prefixes
    assert "&amp;" not in result  # No HTML-encoded ampersands
    assert (
        "%3B" not in result or ";" not in result
    )  # Either encoded or unencoded, not mixed

    expected_parts = ["dataset=planning", "entity=115%3B00041", "field=entry-date"]
    for part in expected_parts:
        assert part in result
def test_is_past_date():
    """
    Tests `is_past_date()` only returns True when a date object passed
    as an argument is in the past.
    """
    today = datetime.today()

    # Assert with a end-date in the future
    end_date_two_years_in_future = (today + relativedelta(years=2)).date()
    result = is_past_date(end_date_two_years_in_future)
    assert result is False

    # Assert with today's date
    end_date_is_today = today.date()
    result = is_past_date(end_date_is_today)
    assert result is False

    # Assert with a end-date in the past
    end_date_three_years_in_past = (today - relativedelta(years=3)).date()
    result = is_past_date(end_date_three_years_in_past)
    assert result is True
