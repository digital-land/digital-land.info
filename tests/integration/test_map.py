import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient

from application.db.models import DatasetOrm, EntityOrm
from application.db.session import DbSession


class TestMapIntegration:
    """Integration tests for the map router"""

    def test_map_endpoint_returns_200(self, client):
        """Test that the map endpoint returns a 200 status code"""
        response = client.get("/map/")
        assert response.status_code == 200

    def test_map_endpoint_returns_html(self, client):
        """Test that the map endpoint returns HTML content"""
        response = client.get("/map/")
        assert "text/html" in response.headers["content-type"]

    def test_map_endpoint_contains_expected_content(self, client):
        """Test that the map endpoint contains expected HTML content"""
        response = client.get("/map/")
        content = response.text
        assert "national-map.html" in content or "map" in content.lower()

    def test_map_endpoint_with_search_query_parameter(self, client):
        """Test that the map endpoint accepts a search query parameter"""
        response = client.get("/map/?q=SW1A 1AA")
        assert response.status_code == 200

    def test_map_endpoint_with_empty_search_query(self, client):
        """Test that the map endpoint handles empty search query"""
        response = client.get("/map/?q=")
        assert response.status_code == 200

    def test_map_endpoint_with_whitespace_search_query(self, client):
        """Test that the map endpoint handles whitespace in search query"""
        response = client.get("/map/?q=  SW1A 1AA  ")
        assert response.status_code == 200

    @patch("application.routers.map_.search")
    def test_map_endpoint_with_postcode_search(self, mock_search, client):
        """Test map endpoint with postcode search"""
        # Mock the OS API search response
        mock_search.return_value = [
            {
                "POSTCODE": "SW1A 1AA",
                "LAT": 51.501009,
                "LNG": -0.124729,
                "ADDRESS": "10 DOWNING STREET, LONDON, SW1A 1AA",
            }
        ]

        response = client.get("/map/?q=SW1A 1AA")
        assert response.status_code == 200

        # Verify the search function was called
        mock_search.assert_called_once_with("SW1A 1AA")

    @patch("application.routers.map_.search")
    def test_map_endpoint_with_uprn_search(self, mock_search, client):
        """Test map endpoint with UPRN search"""
        # Mock the OS API search response
        mock_search.return_value = [
            {
                "UPRN": "123456789",
                "LAT": 51.501009,
                "LNG": -0.124729,
                "ADDRESS": "10 DOWNING STREET, LONDON, SW1A 1AA",
            }
        ]

        response = client.get("/map/?q=123456789")
        assert response.status_code == 200

        # Verify the search function was called
        mock_search.assert_called_once_with("123456789")

    @patch("application.routers.map_.search")
    def test_map_endpoint_with_invalid_search(self, mock_search, client):
        """Test map endpoint with invalid search query"""
        # Mock the OS API search response to return no results
        mock_search.return_value = []

        response = client.get("/map/?q=INVALID123")
        assert response.status_code == 200

        # Verify the search function was called
        mock_search.assert_called_once_with("INVALID123")

    @patch("application.routers.map_.search")
    def test_map_endpoint_with_none_search_response(self, mock_search, client):
        """Test map endpoint when search returns None"""
        # Mock the OS API search response to return None
        mock_search.return_value = None

        response = client.get("/map/?q=INVALID123")
        assert response.status_code == 200

        # Verify the search function was called
        mock_search.assert_called_once_with("INVALID123")

    def test_map_endpoint_with_geography_datasets(self, client, db_session):
        """Test that the map endpoint includes geography datasets"""
        # Create test datasets with entities
        dataset = DatasetOrm(
            dataset="test-geography-dataset",
            typology="geography",
            name="Test Geography Dataset",
            plural="Test Geography Datasets",
        )
        entity = EntityOrm(
            entity=1,
            dataset="test-geography-dataset",
            typology="geography",
        )

        db_session.add(dataset)
        db_session.add(entity)
        db_session.commit()

        response = client.get("/map/")
        assert response.status_code == 200

    def test_map_endpoint_without_geography_datasets(self, client, db_session):
        """Test that the map endpoint works when no geography datasets exist"""
        # Create a dataset that is not geography typology
        dataset = DatasetOrm(
            dataset="test-category-dataset",
            typology="category",
            name="Test Category Dataset",
            plural="Test Category Datasets",
        )

        db_session.add(dataset)
        db_session.commit()

        response = client.get("/map/")
        assert response.status_code == 200

    def test_map_endpoint_with_dataset_but_no_entities(self, client, db_session):
        """Test that the map endpoint works when geography dataset has no entities"""
        # Create a geography dataset but no entities
        dataset = DatasetOrm(
            dataset="test-geography-dataset-no-entities",
            typology="geography",
            name="Test Geography Dataset No Entities",
            plural="Test Geography Datasets No Entities",
        )

        db_session.add(dataset)
        db_session.commit()

        response = client.get("/map/")
        assert response.status_code == 200

    @patch("application.routers.map_.get_datasets_with_data_by_geography")
    def test_map_endpoint_calls_get_datasets_with_data_by_geography(
        self, mock_get_datasets, client, db_session
    ):
        """Test that the map endpoint calls get_datasets_with_data_by_geography"""
        # Mock the function to return empty list
        mock_get_datasets.return_value = []

        response = client.get("/map/")
        assert response.status_code == 200

        # Verify the function was called with DbSession
        mock_get_datasets.assert_called_once()
        call_args = mock_get_datasets.call_args[0][0]
        assert isinstance(call_args, DbSession)

    def test_map_endpoint_headers(self, client):
        """Test that the map endpoint returns appropriate headers"""
        response = client.get("/map/")

        # Check for security headers
        assert "X-Frame-Options" in response.headers
        assert "X-Content-Type-Options" in response.headers
        assert "Strict-Transport-Security" in response.headers

    def test_map_endpoint_cors_headers(self, client):
        """Test that the map endpoint includes CORS headers"""
        response = client.get("/map/", headers={"Origin": "localhost"})
        assert "Access-Control-Allow-Origin" in response.headers

    @patch("application.routers.map_.search")
    def test_map_endpoint_search_result_structure(self, mock_search, client):
        """Test that the search result has the correct structure when search succeeds"""
        # Mock the OS API search response
        mock_search.return_value = [
            {
                "POSTCODE": "SW1A 1AA",
                "LAT": 51.501009,
                "LNG": -0.124729,
                "ADDRESS": "10 DOWNING STREET, LONDON, SW1A 1AA",
            }
        ]

        response = client.get("/map/?q=SW1A 1AA")
        assert response.status_code == 200

        # The response should contain the search query in the HTML
        content = response.text
        assert "SW1A 1AA" in content

    @patch("application.routers.map_.search")
    def test_map_endpoint_search_result_structure_uprn(self, mock_search, client):
        """Test that the search result has the correct structure for UPRN search"""
        # Mock the OS API search response
        mock_search.return_value = [
            {
                "UPRN": "123456789",
                "LAT": 51.501009,
                "LNG": -0.124729,
                "ADDRESS": "10 DOWNING STREET, LONDON, SW1A 1AA",
            }
        ]

        response = client.get("/map/?q=123456789")
        assert response.status_code == 200

        # The response should contain the search query in the HTML
        content = response.text
        assert "123456789" in content

    def test_map_endpoint_multiple_query_parameters(self, client):
        """Test that the map endpoint handles multiple query parameters"""
        response = client.get("/map/?q=SW1A 1AA&other_param=value")
        assert response.status_code == 200

    def test_map_endpoint_special_characters_in_query(self, client):
        """Test that the map endpoint handles special characters in query"""
        response = client.get("/map/?q=SW1A%201AA")
        assert response.status_code == 200

    @patch("application.routers.map_.search")
    def test_map_endpoint_search_with_coordinates(self, mock_search, client):
        """Test that the search result includes coordinates when search succeeds"""
        # Mock the OS API search response with coordinates
        mock_search.return_value = [
            {
                "POSTCODE": "SW1A 1AA",
                "LAT": 51.501009,
                "LNG": -0.124729,
                "ADDRESS": "10 DOWNING STREET, LONDON, SW1A 1AA",
            }
        ]

        response = client.get("/map/?q=SW1A 1AA")
        assert response.status_code == 200

        # The response should contain coordinate information
        content = response.text
        # Check for coordinate values in the response
        assert "51.501009" in content or "-0.124729" in content

    def test_map_endpoint_robustness_with_malformed_query(self, client):
        """Test that the map endpoint is robust with malformed query parameters"""
        # Test with various malformed query parameters
        malformed_queries = [
            "/map/?q=",
            "/map/?q=   ",
            "/map/?q=%20%20",
            "/map/?q=null",
            "/map/?q=undefined",
        ]

        for query in malformed_queries:
            response = client.get(query)
            assert response.status_code == 200, f"Failed for query: {query}"

    @patch("application.routers.map_.search")
    def test_map_endpoint_search_error_handling(self, mock_search, client):
        """Test that the map endpoint handles search errors gracefully"""
        # Mock the search function to raise an exception
        mock_search.side_effect = Exception("Search API error")

        response = client.get("/map/?q=SW1A 1AA")
        assert (
            response.status_code == 200
        )  # Should still return 200 even if search fails
