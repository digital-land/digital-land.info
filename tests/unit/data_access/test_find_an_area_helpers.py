from unittest.mock import patch
from application.data_access.find_an_area_helpers import find_an_area


@patch("application.data_access.find_an_area_helpers.search")
def test_find_an_area_uprn_success(mock_search):
    mock_search.return_value = [
        {"UPRN": "1234567890", "LNG": -0.123, "LAT": 51.5, "POSTCODE": "AB1 2CD"}
    ]
    result = find_an_area("1234567890")
    assert result["type"] == "uprn"
    assert result["query"] == "1234567890"
    assert result["result"]["UPRN"] == "1234567890"
    assert result["geometry"]["name"] == "1234567890"
    assert result["geometry"]["data"]["coordinates"] == [-0.123, 51.5]
    assert result["geometry"]["data"]["properties"]["name"] == "1234567890"


@patch("application.data_access.find_an_area_helpers.search")
def test_find_an_area_postcode_success(mock_search):
    mock_search.return_value = [
        {"UPRN": "9876543210", "LNG": 0.456, "LAT": 52.1, "POSTCODE": "ZZ9 9ZZ"}
    ]
    result = find_an_area("ZZ9 9ZZ")
    assert result["type"] == "postcode"
    assert result["query"] == "ZZ9 9ZZ"
    assert result["result"]["POSTCODE"] == "ZZ9 9ZZ"
    assert result["geometry"]["name"] == "ZZ9 9ZZ"
    assert result["geometry"]["data"]["coordinates"] == [0.456, 52.1]
    assert result["geometry"]["data"]["properties"]["name"] == "ZZ9 9ZZ"


@patch("application.data_access.find_an_area_helpers.search")
def test_find_an_area_selects_middle_item_when_more_than_two(mock_search):
    """
    Tests that when there are more than 2 search results it returns the middle
    item.
    """
    mock_search.return_value = [
        {
            "UPRN": "10010001",
            "ADDRESS": "Flat 1, Summer Street",
            "LNG": 0.2,
            "LAT": 2.2,
            "POSTCODE": "ZZ9 9ZZ",
        },
        {
            "UPRN": "10010002",
            "ADDRESS": "Flat 2, Summer Street",
            "LNG": 0.2,
            "LAT": 2.2,
            "POSTCODE": "ZZ9 9ZZ",
        },
        {
            "UPRN": "10010003",
            "ADDRESS": "Flat 3, Summer Street",
            "LNG": 0.2,
            "LAT": 2.2,
            "POSTCODE": "ZZ9 9ZZ",
        },
    ]
    # Query is non-numeric, so type will be 'postcode' and name comes
    # from POSTCODE
    result = find_an_area("ZZ9 9ZZ")
    assert result["type"] == "postcode"
    assert result["query"] == "ZZ9 9ZZ"
    assert result["result"]["UPRN"] == "10010002"
    assert result["result"]["ADDRESS"] == "Flat 2, Summer Street"
    assert result["geometry"]["name"] == "ZZ9 9ZZ"
    assert result["geometry"]["data"]["coordinates"] == [0.2, 2.2]


@patch("application.data_access.find_an_area_helpers.search")
def test_find_an_area_selects_first_item_when_only_two_results(mock_search):
    """
    Tests that when there are only 2 results, the first item is returned.
    """
    mock_search.return_value = [
        {
            "UPRN": "10010001",
            "ADDRESS": "40, Winter Road",
            "LNG": 0.1,
            "LAT": 1.1,
            "POSTCODE": "AB1 2CD",
        },
        {
            "UPRN": "10010002",
            "ADDRESS": "41, Winter Road",
            "LNG": 0.2,
            "LAT": 1.2,
            "POSTCODE": "AB1 2CD",
        },
    ]
    result = find_an_area("AB1 2CD")
    assert result["type"] == "postcode"
    assert result["query"] == "AB1 2CD"
    assert result["result"]["UPRN"] == "10010001"
    assert result["result"]["ADDRESS"] == "40, Winter Road"
    assert result["geometry"]["name"] == "AB1 2CD"
    assert result["geometry"]["data"]["coordinates"] == [0.1, 1.1]


@patch("application.data_access.find_an_area_helpers.search")
def test_find_an_area_no_results(mock_search):
    mock_search.return_value = []
    result = find_an_area("SUPER CITY", "lpa")
    assert result["type"] == "lpa"
    assert result["query"] == "SUPER CITY"
    assert result["result"] is None
    assert result["geometry"] is None


@patch("application.data_access.find_an_area_helpers.search")
def test_find_an_area_search_exception(mock_search):
    mock_search.side_effect = Exception("API error")
    result = find_an_area("ERRORCASE")
    assert result is None
