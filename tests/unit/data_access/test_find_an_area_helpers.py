from unittest.mock import patch
from application.data_access.find_an_area_helpers import find_an_area

def test_find_an_area_empty_query():
    assert find_an_area("") is None
    assert find_an_area("   ") is None

@patch("application.data_access.find_an_area_helpers.search")
def test_find_an_area_uprn_success(mock_search):
    mock_search.return_value = [{
        "UPRN": "1234567890",
        "LNG": -0.123,
        "LAT": 51.5,
        "POSTCODE": "AB1 2CD"
    }]
    result = find_an_area("1234567890")
    assert result["type"] == "uprn"
    assert result["query"] == "1234567890"
    assert result["result"]["UPRN"] == "1234567890"
    assert result["geometry"]["name"] == "1234567890"
    assert result["geometry"]["data"]["coordinates"] == [-0.123, 51.5]
    assert result["geometry"]["data"]["properties"]["name"] == "1234567890"

@patch("application.data_access.find_an_area_helpers.search")
def test_find_an_area_postcode_success(mock_search):
    mock_search.return_value = [{
        "UPRN": "9876543210",
        "LNG": 0.456,
        "LAT": 52.1,
        "POSTCODE": "ZZ9 9ZZ"
    }]
    result = find_an_area("ZZ9 9ZZ")
    assert result["type"] == "postcode"
    assert result["query"] == "ZZ9 9ZZ"
    assert result["result"]["POSTCODE"] == "ZZ9 9ZZ"
    assert result["geometry"]["name"] == "ZZ9 9ZZ"
    assert result["geometry"]["data"]["coordinates"] == [0.456, 52.1]
    assert result["geometry"]["data"]["properties"]["name"] == "ZZ9 9ZZ"

@patch("application.data_access.find_an_area_helpers.search")
def test_find_an_area_no_results(mock_search):
    mock_search.return_value = []
    result = find_an_area("SOMEQUERY")
    assert result["type"] == "postcode"
    assert result["query"] == "SOMEQUERY"
    assert result["result"] is None
    assert result["geometry"] is None

@patch("application.data_access.find_an_area_helpers.search")
def test_find_an_area_search_exception(mock_search):
    mock_search.side_effect = Exception("API error")
    result = find_an_area("ERRORCASE")
    assert result is None