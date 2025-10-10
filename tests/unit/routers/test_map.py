import pytest
from unittest.mock import Mock, patch
from fastapi import Request

from application.routers.map_ import get_map
from application.core.models import DatasetModel
from application.db.session import DbSession


@pytest.fixture
def mock_request():
    """Create a mock request object"""
    request = Mock(spec=Request)
    request.query_params = Mock()
    return request


@pytest.fixture
def mock_session():
    """Create a mock database session"""
    return Mock()


@pytest.fixture
def mock_redis():
    """Create a mock Redis client"""
    return Mock()


@pytest.fixture
def mock_settings():
    """Create a mock settings object"""
    settings = Mock()
    return settings


@pytest.fixture
def mock_geography_datasets():
    """Create mock geography datasets"""
    return [
        DatasetModel(
            collection="ancient-woodland",
            dataset="ancient-woodland",
            name="Ancient woodland",
            plural="Ancient woodlands",
            typology="geography",
        ),
        DatasetModel(
            collection="conservation-area",
            dataset="conservation-area",
            name="Conservation area",
            plural="Conservation areas",
            typology="geography",
        ),
    ]


@pytest.fixture
def mock_search_response_postcode():
    """Mock OS API search response for postcode"""
    return [
        {
            "POSTCODE": "SW1A 1AA",
            "LAT": 51.501009,
            "LNG": -0.124729,
            "ADDRESS": "10 DOWNING STREET, LONDON, SW1A 1AA",
        }
    ]


@pytest.fixture
def mock_search_response_uprn():
    """Mock OS API search response for UPRN"""
    return [
        {
            "UPRN": "123456789",
            "LAT": 51.501009,
            "LNG": -0.124729,
            "ADDRESS": "10 DOWNING STREET, LONDON, SW1A 1AA",
        }
    ]


@pytest.fixture
def mock_find_an_area(type: str = 'postcode', search_query: str = 'SW1A 1AA'):
    """Mock find_an_area function"""
    return {
        "type": type,
        "query": search_query,
        "result": mock_search_response_postcode[0] if type == 'postcode' else mock_search_response_uprn[0],
        "geometry": {
            "name": "SW1A 1AA",
            "type": "point",
            "data": {
                "type": "Point",
                "coordinates": [-0.124729, 51.501009],
                "properties": {
                    **(mock_search_response_postcode[0] if type == 'postcode' else mock_search_response_uprn[0]),
                    "name": "SW1A 1AA",
                },
            },
        },
    }


@pytest.fixture
def mock_find_an_area_no_results():
    """Mock find_an_area function with no results"""
    return {
        "type": "postcode",
        "query": "INVALID123",
        "result": None,
        "geometry": None,
    }


@pytest.fixture
def mock_find_an_area_postcode():
    """Mock find_an_area function for postcode search"""
    return {
        "type": "postcode",
        "query": "SW1A 1AA",
        "result": {
            "POSTCODE": "SW1A 1AA",
            "LAT": 51.501009,
            "LNG": -0.124729,
            "ADDRESS": "10 DOWNING STREET, LONDON, SW1A 1AA",
        },
        "geometry": {
            "name": "SW1A 1AA",
            "type": "point",
            "data": {
                "type": "Point",
                "coordinates": [-0.124729, 51.501009],
                "properties": {
                    "POSTCODE": "SW1A 1AA",
                    "LAT": 51.501009,
                    "LNG": -0.124729,
                    "ADDRESS": "10 DOWNING STREET, LONDON, SW1A 1AA",
                    "name": "SW1A 1AA",
                },
            },
        },
    }


@pytest.fixture
def mock_find_an_area_uprn():
    """Mock find_an_area function for UPRN search"""
    return {
        "type": "uprn",
        "query": "123456789",
        "result": {
            "UPRN": "123456789",
            "LAT": 51.501009,
            "LNG": -0.124729,
            "ADDRESS": "10 DOWNING STREET, LONDON, SW1A 1AA",
        },
        "geometry": {
            "name": "123456789",
            "type": "point",
            "data": {
                "type": "Point",
                "coordinates": [-0.124729, 51.501009],
                "properties": {
                    "UPRN": "123456789",
                    "LAT": 51.501009,
                    "LNG": -0.124729,
                    "ADDRESS": "10 DOWNING STREET, LONDON, SW1A 1AA",
                    "name": "123456789",
                },
            },
        },
    }

class TestGetMap:
    """Test cases for the get_map function"""

    @patch("application.routers.map_.get_settings")
    @patch("application.routers.map_.get_datasets_with_data_by_geography")
    @patch("application.routers.map_.templates")
    def test_get_map_no_search_query(
        self,
        mock_templates,
        mock_get_datasets,
        mock_get_settings,
        mock_request,
        mock_session,
        mock_redis,
        mock_geography_datasets,
        mock_settings,
    ):
        """Test get_map with no search query parameter"""
        # Setup
        mock_request.query_params.get.return_value = ""
        mock_get_settings.return_value = mock_settings
        mock_get_datasets.return_value = mock_geography_datasets
        mock_template_response = Mock()
        mock_templates.TemplateResponse.return_value = mock_template_response

        # Execute
        result = get_map(mock_request, mock_session, mock_redis)

        # Assert
        mock_request.query_params.get.assert_called_once_with("q", "")
        mock_get_settings.assert_called_once()
        mock_get_datasets.assert_called_once_with(
            DbSession(session=mock_session, redis=mock_redis)
        )
        mock_templates.TemplateResponse.assert_called_once_with(
            "national-map.html",
            {
                "request": mock_request,
                "layers": mock_geography_datasets,
                "settings": mock_settings,
                "search_query": "",
                "search_result": None,
                "feedback_form_footer": True,
            },
        )
        assert result == mock_template_response

    @patch("application.routers.map_.get_settings")
    @patch("application.routers.map_.get_datasets_with_data_by_geography")
    @patch("application.routers.map_.find_an_area")
    @patch("application.routers.map_.templates")
    def test_get_map_with_postcode_search(
        self,
        mock_templates,
        mock_find_an_area,
        mock_get_datasets,
        mock_get_settings,
        mock_request,
        mock_session,
        mock_redis,
        mock_geography_datasets,
        mock_search_response_postcode,
        mock_settings,
        mock_find_an_area_postcode,
    ):
        """Test get_map with postcode search query"""
        # Setup
        search_query = "SW1A 1AA"
        mock_request.query_params.get.return_value = search_query
        mock_get_settings.return_value = mock_settings
        mock_get_datasets.return_value = mock_geography_datasets
        mock_find_an_area.return_value = mock_find_an_area_postcode
        mock_template_response = Mock()
        mock_templates.TemplateResponse.return_value = mock_template_response

        # Execute
        result = get_map(mock_request, mock_session, mock_redis)

        # Assert
        mock_find_an_area.assert_called_once_with(search_query)
        mock_templates.TemplateResponse.assert_called_once_with(
            "national-map.html",
            {
                "request": mock_request,
                "layers": mock_geography_datasets,
                "settings": mock_settings,
                "search_query": search_query,
                "search_result": {
                    "type": "postcode",
                    "query": search_query,
                    "result": mock_search_response_postcode[0],
                    "geometry": {
                        "name": "SW1A 1AA",
                        "type": "point",
                        "data": {
                            "type": "Point",
                            "coordinates": [-0.124729, 51.501009],
                            "properties": {
                                **mock_search_response_postcode[0],
                                "name": "SW1A 1AA",
                            },
                        },
                    },
                },
                "feedback_form_footer": True,
            },
        )
        assert result == mock_template_response

    @patch("application.routers.map_.get_settings")
    @patch("application.routers.map_.get_datasets_with_data_by_geography")
    @patch("application.routers.map_.find_an_area")
    @patch("application.routers.map_.templates")
    def test_get_map_with_uprn_search(
        self,
        mock_templates,
        mock_find_an_area,
        mock_get_datasets,
        mock_get_settings,
        mock_request,
        mock_session,
        mock_redis,
        mock_geography_datasets,
        mock_search_response_uprn,
        mock_settings,
        mock_find_an_area_uprn,
    ):
        """Test get_map with UPRN search query"""
        # Setup
        search_query = "123456789"
        mock_request.query_params.get.return_value = search_query
        mock_get_settings.return_value = mock_settings
        mock_get_datasets.return_value = mock_geography_datasets
        mock_find_an_area.return_value = mock_find_an_area_uprn
        mock_template_response = Mock()
        mock_templates.TemplateResponse.return_value = mock_template_response

        # Execute
        result = get_map(mock_request, mock_session, mock_redis)

        # Assert
        mock_find_an_area.assert_called_once_with(search_query)
        mock_templates.TemplateResponse.assert_called_once_with(
            "national-map.html",
            {
                "request": mock_request,
                "layers": mock_geography_datasets,
                "settings": mock_settings,
                "search_query": search_query,
                "search_result": {
                    "type": "uprn",
                    "query": search_query,
                    "result": mock_search_response_uprn[0],
                    "geometry": {
                        "name": "123456789",
                        "type": "point",
                        "data": {
                            "type": "Point",
                            "coordinates": [-0.124729, 51.501009],
                            "properties": {
                                **mock_search_response_uprn[0],
                                "name": "123456789",
                            },
                        },
                    },
                },
                "feedback_form_footer": True,
            },
        )
        assert result == mock_template_response

    @patch("application.routers.map_.get_settings")
    @patch("application.routers.map_.get_datasets_with_data_by_geography")
    @patch("application.routers.map_.find_an_area")
    @patch("application.routers.map_.templates")
    def test_get_map_with_search_no_results(
        self,
        mock_templates,
        mock_find_an_area,
        mock_get_datasets,
        mock_get_settings,
        mock_request,
        mock_session,
        mock_redis,
        mock_geography_datasets,
        mock_settings,
        mock_find_an_area_no_results,
    ):
        """Test get_map with search query that returns no results"""
        # Setup
        search_query = "INVALID123"
        mock_request.query_params.get.return_value = search_query
        mock_get_settings.return_value = mock_settings
        mock_get_datasets.return_value = mock_geography_datasets
        mock_find_an_area.return_value = mock_find_an_area_no_results
        mock_template_response = Mock()
        mock_templates.TemplateResponse.return_value = mock_template_response

        # Execute
        result = get_map(mock_request, mock_session, mock_redis)

        # Assert
        mock_find_an_area.assert_called_once_with(search_query)
        mock_templates.TemplateResponse.assert_called_once_with(
            "national-map.html",
            {
                "request": mock_request,
                "layers": mock_geography_datasets,
                "settings": mock_settings,
                "search_query": search_query,
                "search_result": {
                    "type": "postcode",
                    "query": search_query,
                    "result": None,
                    "geometry": None,
                },
                "feedback_form_footer": True,
            },
        )
        assert result == mock_template_response

    @patch("application.routers.map_.get_settings")
    @patch("application.routers.map_.get_datasets_with_data_by_geography")
    @patch("application.routers.map_.find_an_area")
    @patch("application.routers.map_.templates")
    def test_get_map_with_search_none_response(
        self,
        mock_templates,
        mock_find_an_area,
        mock_get_datasets,
        mock_get_settings,
        mock_request,
        mock_session,
        mock_redis,
        mock_geography_datasets,
        mock_settings,
        mock_find_an_area_no_results,
    ):
        """Test get_map with search query that returns None"""
        # Setup
        search_query = "INVALID123"
        mock_request.query_params.get.return_value = search_query
        mock_get_settings.return_value = mock_settings
        mock_get_datasets.return_value = mock_geography_datasets
        mock_find_an_area.return_value = mock_find_an_area_no_results
        mock_template_response = Mock()
        mock_templates.TemplateResponse.return_value = mock_template_response

        # Execute
        result = get_map(mock_request, mock_session, mock_redis)

        # Assert
        mock_find_an_area.assert_called_once_with(search_query)
        mock_templates.TemplateResponse.assert_called_once_with(
            "national-map.html",
            {
                "request": mock_request,
                "layers": mock_geography_datasets,
                "settings": mock_settings,
                "search_query": search_query,
                "search_result": {
                    "type": "postcode",
                    "query": search_query,
                    "result": None,
                    "geometry": None,
                },
                "feedback_form_footer": True,
            },
        )
        assert result == mock_template_response

    @patch("application.routers.map_.get_settings")
    @patch("application.routers.map_.get_datasets_with_data_by_geography")
    @patch("application.routers.map_.find_an_area")
    @patch("application.routers.map_.templates")
    def test_get_map_with_whitespace_search_query(
        self,
        mock_templates,
        mock_find_an_area,
        mock_get_datasets,
        mock_get_settings,
        mock_request,
        mock_session,
        mock_redis,
        mock_geography_datasets,
        mock_settings,
        mock_find_an_area_no_results,
    ):
        """Test get_map with search query that has whitespace"""
        # Setup
        search_query = "  SW1A 1AA  "
        mock_request.query_params.get.return_value = search_query
        mock_get_settings.return_value = mock_settings
        mock_get_datasets.return_value = mock_geography_datasets
        mock_find_an_area.return_value = {
            "type": "postcode",
            "query": "SW1A 1AA",
            "result": None,
            "geometry": None,
        }
        mock_template_response = Mock()
        mock_templates.TemplateResponse.return_value = mock_template_response

        # Execute
        result = get_map(mock_request, mock_session, mock_redis)

        # Assert
        mock_find_an_area.assert_called_once_with("SW1A 1AA")  # Should be stripped
        mock_templates.TemplateResponse.assert_called_once_with(
            "national-map.html",
            {
                "request": mock_request,
                "layers": mock_geography_datasets,
                "settings": mock_settings,
                "search_query": "SW1A 1AA",  # Should be stripped
                "search_result": {
                    "type": "postcode",
                    "query": "SW1A 1AA",
                    "result": None,
                    "geometry": None,
                },
                "feedback_form_footer": True,
            },
        )
        assert result == mock_template_response

    @patch("application.routers.map_.get_settings")
    @patch("application.routers.map_.get_datasets_with_data_by_geography")
    @patch("application.data_access.find_an_area_helpers.find_an_area")
    @patch("application.routers.map_.templates")
    def test_get_map_with_empty_search_query_after_strip(
        self,
        mock_templates,
        mock_find_an_area,
        mock_get_datasets,
        mock_get_settings,
        mock_request,
        mock_session,
        mock_redis,
        mock_geography_datasets,
        mock_settings,
    ):
        """Test get_map with search query that becomes empty after stripping"""
        # Setup
        search_query = "   "
        mock_request.query_params.get.return_value = search_query
        mock_get_settings.return_value = mock_settings
        mock_get_datasets.return_value = mock_geography_datasets
        mock_find_an_area.return_value = mock_find_an_area_no_results
        mock_template_response = Mock()
        mock_templates.TemplateResponse.return_value = mock_template_response

        # Execute
        result = get_map(mock_request, mock_session, mock_redis)

        # Assert
        mock_find_an_area.assert_not_called()  # Should not be called for empty query
        mock_templates.TemplateResponse.assert_called_once_with(
            "national-map.html",
            {
                "request": mock_request,
                "layers": mock_geography_datasets,
                "settings": mock_settings,
                "search_query": "",
                "search_result": None,
                "feedback_form_footer": True,
            },
        )
        assert result == mock_template_response
