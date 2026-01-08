from unittest.mock import patch, Mock, MagicMock
import os

from application.data_access.os_api import (
    search,
    search_postcode,
    search_uprn,
    transform_search_results,
    is_valid_postcode,
    get_os_api_key,
    base_search_params,
    search_local_planning_authority,
)


class TestOSAPI:
    """Test cases for OS API functionality"""

    @patch("application.data_access.os_api.get_os_api_key")
    def test_get_os_api_key_returns_env_variable(self, mock_getenv):
        """Test that get_os_api_key returns the OS_CLIENT_KEY environment variable"""
        mock_getenv.return_value = "test-api-key"

        with patch.dict(os.environ, {"OS_CLIENT_KEY": "test-api-key"}):
            result = get_os_api_key()
            assert result == "test-api-key"

    @patch("application.data_access.os_api.get_os_api_key")
    def test_base_search_params_includes_api_key(self, mock_get_api_key):
        """Test that base_search_params includes the API key"""
        mock_get_api_key.return_value = "test-api-key"

        params = base_search_params()
        assert params["key"] == "test-api-key"
        assert params["output_srs"] == "WGS84"

    @patch("application.data_access.os_api.requests.get")
    @patch("application.data_access.os_api.base_search_params")
    def test_search_postcode_calls_correct_endpoint(self, mock_base_params, mock_get):
        """Test that search_postcode calls the correct OS API endpoint"""
        mock_base_params.return_value = {"key": "test-key", "output_srs": "WGS84"}
        mock_response = Mock()
        mock_response.json.return_value = {"results": []}
        mock_get.return_value = mock_response

        search_postcode("SW1A 1AA")

        mock_get.assert_called_once_with(
            "https://api.os.uk/search/places/v1/postcode",
            params={"key": "test-key", "output_srs": "WGS84", "postcode": "SW1A 1AA"},
        )

    @patch("application.data_access.os_api.requests.get")
    @patch("application.data_access.os_api.base_search_params")
    def test_search_uprn_calls_correct_endpoint(self, mock_base_params, mock_get):
        """Test that search_uprn calls the correct OS API endpoint"""
        mock_base_params.return_value = {"key": "test-key", "output_srs": "WGS84"}
        mock_response = Mock()
        mock_response.json.return_value = {"results": []}
        mock_get.return_value = mock_response

        search_uprn("123456789")

        mock_get.assert_called_once_with(
            "https://api.os.uk/search/places/v1/uprn",
            params={"key": "test-key", "output_srs": "WGS84", "uprn": "123456789"},
        )

    def test_transform_search_results_with_valid_data(self):
        """Test that transform_search_results correctly transforms valid data"""
        input_data = {
            "results": [
                {"DPA": {"POSTCODE": "SW1A 1AA", "LAT": 51.501009, "LNG": -0.124729}},
                {"DPA": {"POSTCODE": "SW1A 2AA", "LAT": 51.501010, "LNG": -0.124730}},
            ]
        }

        result = transform_search_results(input_data)

        assert len(result) == 2
        assert result[0]["POSTCODE"] == "SW1A 1AA"
        assert result[0]["LAT"] == 51.501009
        assert result[0]["LNG"] == -0.124729
        assert result[1]["POSTCODE"] == "SW1A 2AA"

    def test_transform_search_results_with_empty_results(self):
        """Test that transform_search_results handles empty results"""
        input_data = {"results": []}

        result = transform_search_results(input_data)

        assert result == []

    def test_transform_search_results_with_missing_dpa(self):
        """Test that transform_search_results handles missing DPA data"""
        input_data = {
            "results": [
                {"DPA": {"POSTCODE": "SW1A 1AA"}},
                {"OTHER": "data"},  # Missing DPA
            ]
        }

        result = transform_search_results(input_data)

        assert len(result) == 2
        assert result[0]["POSTCODE"] == "SW1A 1AA"
        assert result[1] == {}  # Empty dict for missing DPA

    def test_transform_search_results_with_none_results(self):
        """Test that transform_search_results handles None results"""
        input_data = {"results": None}

        result = transform_search_results(input_data)

        assert result == []

    def test_is_valid_postcode_valid_formats(self):
        """Test that is_valid_postcode correctly validates valid postcode formats"""
        valid_postcodes = [
            "SW1A 1AA",
            "M1 1AA",
            "B33 8TH",
            "CR2 6XH",
            "DN55 1PT",
            "W1A 0AX",
            "EC1A 1BB",
        ]

        for postcode in valid_postcodes:
            assert is_valid_postcode(postcode), f"Postcode {postcode} should be valid"

    def test_is_valid_postcode_invalid_formats(self):
        """Test that is_valid_postcode correctly rejects invalid postcode formats"""
        invalid_postcodes = [
            "INVALID",
            "12345",
            "SW1A",
            "SW1A 1",
            "SW1A 1A",
            "SW1A 1AAA",
            "SW1AA 1AA",
            "",
            "   ",
        ]

        for postcode in invalid_postcodes:
            assert not is_valid_postcode(
                postcode
            ), f"Postcode {postcode} should be invalid"

    def test_is_valid_postcode_case_insensitive(self):
        """Test that is_valid_postcode is case insensitive"""
        postcodes = [
            "sw1a 1aa",
            "SW1A 1AA",
            "Sw1A 1Aa",
        ]

        for postcode in postcodes:
            assert is_valid_postcode(postcode), f"Postcode {postcode} should be valid"

    @patch("application.data_access.os_api.search_postcode")
    def test_search_with_valid_postcode(self, mock_search_postcode):
        """Test that search calls search_postcode for valid postcodes"""
        mock_search_postcode.return_value = {
            "results": [{"DPA": {"POSTCODE": "SW1A 1AA"}}]
        }

        result = search("SW1A 1AA", "postcode")

        mock_search_postcode.assert_called_once_with("SW1A 1AA")
        assert result == [{"POSTCODE": "SW1A 1AA"}]

    @patch("application.data_access.os_api.search_uprn")
    def test_search_with_numeric_uprn(self, mock_search_uprn):
        """Test that search calls search_uprn for numeric queries"""
        mock_search_uprn.return_value = {"results": [{"DPA": {"UPRN": "123456789"}}]}

        result = search("123456789", "uprn")

        mock_search_uprn.assert_called_once_with("123456789")
        assert result == [{"UPRN": "123456789"}]

    def test_search_with_empty_query(self):
        """Test that search returns empty list for empty query"""
        result = search("", "")
        assert result == []

    @patch("application.data_access.os_api.search_postcode")
    def test_search_with_postcode_returns_none(self, mock_search_postcode):
        """Test that search handles None response from search_postcode"""
        mock_search_postcode.return_value = None

        result = search("SW1A 1AA", "postcode")

        assert result == []

    @patch("application.data_access.os_api.search_uprn")
    def test_search_with_uprn_returns_none(self, mock_search_uprn):
        """Test that search handles None response from search_uprn"""
        mock_search_uprn.return_value = None

        result = search("123456789", "uprn")

        assert result == []

    @patch("application.data_access.os_api.search_postcode")
    def test_search_with_postcode_returns_empty_results(self, mock_search_postcode):
        """Test that search handles empty results from search_postcode"""
        mock_search_postcode.return_value = {"results": []}

        result = search("SW1A 1AA", "postcode")

        assert result == []

    @patch("application.data_access.os_api.search_uprn")
    def test_search_with_uprn_returns_empty_results(self, mock_search_uprn):
        """Test that search handles empty results from search_uprn"""
        mock_search_uprn.return_value = {"results": []}

        result = search("123456789", "uprn")

        assert result == []

    @patch("application.data_access.os_api.search_postcode")
    def test_search_with_postcode_returns_malformed_data(self, mock_search_postcode):
        """Test that search handles malformed data from search_postcode"""
        mock_search_postcode.return_value = {"malformed": "data"}

        result = search("SW1A 1AA", "postcode")

        assert result == []

    @patch("application.data_access.os_api.search_uprn")
    def test_search_with_uprn_returns_malformed_data(self, mock_search_uprn):
        """Test that search handles malformed data from search_uprn"""
        mock_search_uprn.return_value = {"malformed": "data"}

        result = search("123456789", "uprn")

        assert result == []

    def test_search_edge_cases(self):
        """Test search with various edge cases"""
        # Test with very long numeric string (should be treated as UPRN)
        with patch("application.data_access.os_api.search_uprn") as mock_search_uprn:
            mock_search_uprn.return_value = {"results": []}
            search("12345678901234567890", "uprn")
            mock_search_uprn.assert_called_once_with("12345678901234567890")

        # Test with mixed alphanumeric (should be treated as postcode)
        with patch(
            "application.data_access.os_api.search_postcode"
        ) as mock_search_postcode:
            mock_search_postcode.return_value = {"results": []}
            search("A1B 2CD", "postcode")  # Valid postcode format: A1B 2CD
            mock_search_postcode.assert_called_once_with("A1B 2CD")

    @patch("application.data_access.os_api.get_entity_map_lpa")
    @patch("application.data_access.os_api.get_context_session")
    def test_search_local_planning_authority_returns_serialised_results(
        self, mock_get_context_session, mock_get_entity_map_lpa
    ):
        context_manager = MagicMock()
        mock_session = MagicMock()
        context_manager.__enter__.return_value = mock_session
        context_manager.__exit__.return_value = None
        mock_get_context_session.return_value = context_manager

        # Mock EntityModel object with a dict() method
        mock_entity = MagicMock()
        mock_entity.dict.return_value = {
            "entity": 1,
            "name": "Manchester LPA",
            "dataset": "local-planning-authority",
        }
        mock_get_entity_map_lpa.return_value = mock_entity

        results = search_local_planning_authority("Manchester")

        mock_get_entity_map_lpa.assert_called_once_with(
            mock_session, {"name": "Manchester"}
        )
        assert results == {
            "entity": 1,
            "name": "Manchester LPA",
            "dataset": "local-planning-authority",
        }

    @patch("application.data_access.os_api.get_entity_map_lpa")
    @patch("application.data_access.os_api.get_context_session")
    def test_search_local_planning_authority_returns_empty_results(
        self, mock_get_context_session, mock_get_entity_map_lpa
    ):
        context_manager = MagicMock()
        mock_session = MagicMock()
        context_manager.__enter__.return_value = mock_session
        context_manager.__exit__.return_value = None
        mock_get_context_session.return_value = context_manager

        # Mock that get_entity_map_lpa raises AttributeError
        mock_get_entity_map_lpa.side_effect = AttributeError(
            "'NoneType' object has no attribute 'json'"
        )

        results = search_local_planning_authority("Super manchester")
        mock_get_entity_map_lpa.assert_called_once_with(
            mock_session, {"name": "Super manchester"}
        )

        assert results == []

    @patch(
        "application.data_access.os_api.search_local_planning_authority",
        return_value={"entity": 1, "name": "Manchester LPA"},
    )
    def test_search_with_alpha_query_calls_lpa(self, mock_lpa_search):
        result = search("Manchester", "lpa")
        mock_lpa_search.assert_called_once_with("Manchester")
        assert result == [{"entity": 1, "name": "Manchester LPA"}]

    @patch("application.data_access.os_api.requests.get")
    @patch("application.data_access.os_api.base_search_params")
    def test_search_postcode_handles_request_exception(
        self, mock_base_params, mock_get
    ):
        """Test that search_postcode handles request exceptions gracefully"""
        mock_base_params.return_value = {"key": "test-key", "output_srs": "WGS84"}
        mock_get.side_effect = Exception("Network error")

        result = search_postcode("SW1A 1AA")

        assert result is None

    @patch("application.data_access.os_api.requests.get")
    @patch("application.data_access.os_api.base_search_params")
    def test_search_uprn_handles_request_exception(self, mock_base_params, mock_get):
        """Test that search_uprn handles request exceptions gracefully"""
        mock_base_params.return_value = {"key": "test-key", "output_srs": "WGS84"}
        mock_get.side_effect = Exception("Network error")

        result = search_uprn("123456789")

        assert result is None
