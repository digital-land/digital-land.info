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


class IsListOfDicts:
    """
    A helper class to check if an object (layers) is a list of dictionaries.
    """

    def __eq__(self, layers):
        return isinstance(layers, list) and all(isinstance(i, dict) for i in layers)


class TestGetMap:
    """
    Test cases for the get_map function.
    """

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
        mock_settings,
    ):
        """Test `get_map()` with no search query parameter displays the map correctly."""
        # Setup
        mock_get_settings.return_value = mock_settings
        mock_template_response = Mock()
        mock_templates.TemplateResponse.return_value = mock_template_response

        # Execute
        result = get_map(
            mock_request,
            mock_session,
            mock_redis,
            search_query="",
            search_type=None,
        )

        # Assert
        mock_get_settings.assert_called_once()
        mock_get_datasets.assert_called_once_with(
            DbSession(session=mock_session, redis=mock_redis)
        )
        mock_templates.TemplateResponse.assert_called_once_with(
            "national-map.html",
            {
                "request": mock_request,
                "layers": IsListOfDicts(),
                "settings": mock_settings,
                "search_query": "",
                "search_result": None,
                "entity_paint_options": None,
                "feedback_form_footer": True,
            },
        )
        assert result == mock_template_response

    @patch("application.routers.map_.get_settings")
    @patch("application.routers.map_.get_datasets_with_data_by_geography")
    @patch("application.routers.map_.templates")
    def test_get_map_with_invalid_uprn(
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
        """Test `get_map()` with invalid UPRN search query raises error."""

        # Setup
        search_query = "12345ABC"
        search_type = "uprn"
        mock_get_settings.return_value = mock_settings
        mock_get_datasets.return_value = mock_geography_datasets
        mock_template_response = Mock()
        mock_templates.TemplateResponse.return_value = mock_template_response

        # Execute
        result = get_map(
            mock_request,
            mock_session,
            mock_redis,
            search_query,
            search_type,
        )

        # Assert
        mock_templates.TemplateResponse.assert_called_once_with(
            "national-map.html",
            {
                "request": mock_request,
                "layers": IsListOfDicts(),
                "settings": mock_settings,
                "search_query": search_query.strip(),
                "search_result": None,
                "error": "UPRN must be a number",
                "entity_paint_options": None,
                "feedback_form_footer": True,
            },
        )
        assert result == mock_template_response

    @patch("application.routers.map_.get_settings")
    @patch("application.routers.map_.get_datasets_with_data_by_geography")
    @patch("application.routers.map_.templates")
    def test_get_map_with_invalid_uprn_length(
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
        """
        Test `get_map()` with UPRN that is 13 digits length instead a
        a max of 12 raises error.
        """

        # Setup
        search_query = "1234567890123"  # 13 digits instead a max of 12
        search_type = "uprn"
        mock_get_settings.return_value = mock_settings
        mock_get_datasets.return_value = mock_geography_datasets
        mock_template_response = Mock()
        mock_templates.TemplateResponse.return_value = mock_template_response

        # Execute
        result = get_map(
            mock_request,
            mock_session,
            mock_redis,
            search_query,
            search_type,
        )

        # Assert: wrong-length UPRN should trigger validation error
        mock_templates.TemplateResponse.assert_called_once_with(
            "national-map.html",
            {
                "request": mock_request,
                "layers": IsListOfDicts(),
                "settings": mock_settings,
                "search_query": search_query.strip(),
                "search_result": None,
                "error": "UPRN must be 12 digits",
                "entity_paint_options": None,
                "feedback_form_footer": True,
            },
        )
        assert result == mock_template_response

    @patch("application.routers.map_.get_settings")
    @patch("application.routers.map_.get_datasets_with_data_by_geography")
    @patch("application.routers.map_.templates")
    def test_get_map_with_empty_search_query_for_lpa_raises_error(
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
        """Test `get_map()` with empty search query for LPA raises error."""

        # Setup
        search_query = "   "
        search_type = "lpa"
        mock_get_settings.return_value = mock_settings
        mock_get_datasets.return_value = mock_geography_datasets
        mock_template_response = Mock()
        mock_templates.TemplateResponse.return_value = mock_template_response

        # Execute
        result = get_map(
            mock_request,
            mock_session,
            mock_redis,
            search_query,
            search_type,
        )

        # Assert: empty LPA should use the LPA-specific error message from map_.py
        mock_templates.TemplateResponse.assert_called_once_with(
            "national-map.html",
            {
                "request": mock_request,
                "layers": IsListOfDicts(),
                "settings": mock_settings,
                "search_query": "",
                "search_result": None,
                "error": "Select a local planning authority",
                "entity_paint_options": None,
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
        """
        Test `get_map()` with a valid postcode search query displays the search results
        correctly on the map.
        """
        # Setup
        search_query = "SW1A 1AA"
        search_type = "postcode"
        mock_get_settings.return_value = mock_settings
        mock_get_datasets.return_value = mock_geography_datasets
        mock_find_an_area.return_value = mock_find_an_area_postcode
        mock_template_response = Mock()
        mock_templates.TemplateResponse.return_value = mock_template_response

        # Execute
        result = get_map(
            mock_request,
            mock_session,
            mock_redis,
            search_query,
            search_type,
        )

        # Assert
        assert mock_find_an_area.call_count == 1
        assert mock_find_an_area.call_args[0][0] == search_query
        mock_templates.TemplateResponse.assert_called_once_with(
            "national-map.html",
            {
                "request": mock_request,
                "layers": IsListOfDicts(),
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
                "entity_paint_options": None,
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
        """
        Test `get_map()` with a UPRN search query displays the search results
        correctly on the map.
        """
        # Setup
        search_query = "123456789"
        search_type = "uprn"
        mock_get_settings.return_value = mock_settings
        mock_get_datasets.return_value = mock_geography_datasets
        mock_find_an_area.return_value = mock_find_an_area_uprn
        mock_template_response = Mock()
        mock_templates.TemplateResponse.return_value = mock_template_response

        # Execute
        result = get_map(
            mock_request,
            mock_session,
            mock_redis,
            search_query,
            search_type,
        )

        # Assert
        assert mock_find_an_area.call_count == 1
        assert mock_find_an_area.call_args[0][0] == search_query
        mock_templates.TemplateResponse.assert_called_once_with(
            "national-map.html",
            {
                "request": mock_request,
                "layers": IsListOfDicts(),
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
                "entity_paint_options": None,
                "feedback_form_footer": True,
            },
        )
        assert result == mock_template_response

    @patch("application.routers.map_.get_settings")
    @patch("application.routers.map_.get_datasets_with_data_by_geography")
    @patch("application.routers.map_.find_an_area")
    @patch("application.routers.map_.templates")
    def test_get_map_sets_entity_options_when_called_with_valid_lpa(
        self,
        mock_templates,
        mock_find_an_area,
        mock_get_datasets,
        mock_get_settings,
        mock_request,
        mock_session,
        mock_redis,
        mock_settings,
    ):
        """Tests `get_map()` sets entity_paint_options when called with a valid LPA search_query."""
        geography_datasets = [
            DatasetModel(
                collection="other-dataset",
                dataset="other-dataset",
                name="Other dataset",
                plural="Other datasets",
                typology="geography",
                paint_options=None,
            ),
            DatasetModel(
                collection="lpa-collection",
                dataset="local-planning-authority",
                name="Local planning authority",
                plural="Local planning authorities",
                typology="geography",
                paint_options={"foo": "bar"},
            ),
        ]

        search_query = "Some LPA"
        search_type = "lpa"
        mock_get_settings.return_value = mock_settings
        mock_get_datasets.return_value = geography_datasets
        mock_find_an_area.return_value = {
            "type": "lpa",
            "query": search_query,
            "result": {
                "name": "Some LPA",
                "dataset": "local-planning-authority",
                "entity": 123,
                "geojson": {"geometry": {"type": "Polygon", "coordinates": []}},
            },
            "geometry": {
                "name": "Some LPA",
                "type": "geometry",
                "data": {"type": "Polygon", "coordinates": []},
                "entity": 123,
            },
        }

        mock_template_response = Mock()
        mock_templates.TemplateResponse.return_value = mock_template_response

        # Execute
        result = get_map(
            mock_request,
            mock_session,
            mock_redis,
            search_query,
            search_type,
        )

        # Assert
        assert mock_find_an_area.call_count == 1
        assert mock_find_an_area.call_args[0][0] == search_query

        # entity_paint_options should be taken from the matching dataset
        mock_templates.TemplateResponse.assert_called_once_with(
            "national-map.html",
            {
                "request": mock_request,
                "layers": IsListOfDicts(),
                "settings": mock_settings,
                "search_query": search_query,
                "search_result": mock_find_an_area.return_value,
                "entity_paint_options": {"foo": "bar"},
                "feedback_form_footer": True,
            },
        )
        assert result == mock_template_response

    @patch("application.routers.map_.get_settings")
    @patch("application.routers.map_.get_datasets_with_data_by_geography")
    @patch("application.routers.map_.find_an_area")
    @patch("application.routers.map_.templates")
    def test_get_map_infers_postcode_when_type_omitted(
        self,
        mock_templates,
        mock_find_an_area,
        mock_get_datasets,
        mock_get_settings,
        mock_request,
        mock_session,
        mock_redis,
        mock_geography_datasets,
        mock_find_an_area_postcode,
        mock_settings,
    ):
        """
        Tests `get_map()` with a valid postcode search query but without search type
        does not trigger a call to `find_an_area()`
        """
        search_query = "SW1A 1AA"
        search_type = None
        mock_get_settings.return_value = mock_settings
        mock_get_datasets.return_value = mock_geography_datasets
        mock_find_an_area.return_value = mock_find_an_area_postcode
        mock_template_response = Mock()
        mock_templates.TemplateResponse.return_value = mock_template_response

        # Execute
        result = get_map(
            mock_request,
            mock_session,
            mock_redis,
            search_query,
            search_type,
        )

        # Assert: since search_type is None, we do not call find_an_area(), and
        # no search_result is passed to the template.
        mock_find_an_area.assert_not_called()
        mock_templates.TemplateResponse.assert_called_once_with(
            "national-map.html",
            {
                "request": mock_request,
                "layers": IsListOfDicts(),
                "settings": mock_settings,
                "search_query": search_query,
                "search_result": None,
                "entity_paint_options": None,
                "feedback_form_footer": True,
            },
        )
        assert result == mock_template_response

    @patch("application.routers.map_.get_settings")
    @patch("application.routers.map_.get_datasets_with_data_by_geography")
    @patch("application.routers.map_.find_an_area")
    @patch("application.routers.map_.templates")
    def test_get_map_with_an_invalid_postcode_triggers_validation_error(
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
        """Test `get_map()` with an invalid postcode search query raises error."""

        # Setup
        search_query = "INVALID123"  # Not a valid UK postcode
        search_type = "postcode"
        mock_get_settings.return_value = mock_settings
        mock_get_datasets.return_value = mock_geography_datasets
        mock_template_response = Mock()
        mock_templates.TemplateResponse.return_value = mock_template_response

        # Execute
        result = get_map(
            mock_request,
            mock_session,
            mock_redis,
            search_query,
            search_type,
        )

        # Assert: validation should fail, so find_an_area is never called
        mock_find_an_area.assert_not_called()
        mock_templates.TemplateResponse.assert_called_once_with(
            "national-map.html",
            {
                "request": mock_request,
                "layers": IsListOfDicts(),
                "settings": mock_settings,
                "search_query": search_query,
                "search_result": None,
                "error": "Enter a full UK postcode",
                "entity_paint_options": None,
                "feedback_form_footer": True,
            },
        )
        assert result == mock_template_response

    @patch("application.routers.map_.get_settings")
    @patch("application.routers.map_.get_datasets_with_data_by_geography")
    @patch("application.routers.map_.find_an_area")
    @patch("application.routers.map_.templates")
    def test_get_map_strips_whitespaces_from_search_query(
        self,
        mock_templates,
        mock_find_an_area,
        mock_get_datasets,
        mock_get_settings,
        mock_request,
        mock_session,
        mock_redis,
        mock_settings,
    ):
        """Test `get_map()` strips whitespaces from search query."""
        # Setup
        search_query = "  SW1A 1AA  "
        search_type = "postcode"
        mock_get_settings.return_value = mock_settings
        mock_find_an_area.return_value = {
            "type": "postcode",
            "query": "SW1A 1AA",
            "result": None,
            "geometry": None,
        }
        mock_template_response = Mock()
        mock_templates.TemplateResponse.return_value = mock_template_response

        # Execute
        result = get_map(
            mock_request, mock_session, mock_redis, search_query, search_type
        )

        # No need to assert the full call signature so the test
        # doesn't depend on whether a second (search_type)
        # argument is passed.
        assert mock_find_an_area.call_count == 1
        assert mock_find_an_area.call_args[0][0] == "SW1A 1AA"

        mock_templates.TemplateResponse.assert_called_once_with(
            "national-map.html",
            {
                "request": mock_request,
                "layers": IsListOfDicts(),
                "settings": mock_settings,
                "search_query": "SW1A 1AA",  # Should be stripped
                "search_result": {
                    "type": "postcode",
                    "query": "SW1A 1AA",
                    "result": None,
                    "geometry": None,
                },
                "entity_paint_options": None,
                "feedback_form_footer": True,
            },
        )
        assert result == mock_template_response

    @patch("application.routers.map_.get_settings")
    @patch("application.routers.map_.get_datasets_with_data_by_geography")
    @patch("application.routers.map_.templates")
    def test_get_map_with_empty_search_query_raises_error(
        self,
        mock_templates,
        mock_get_datasets,
        mock_get_settings,
        mock_request,
        mock_session,
        mock_redis,
        mock_settings,
    ):
        """
        Test `get_map()` with an empty postcode search query will raise error.
        """
        # Setup
        search_query = "   "
        search_type = "postcode"
        mock_get_settings.return_value = mock_settings
        mock_get_datasets.return_value = [
            DatasetModel(
                collection="ancient-woodland",
                dataset="ancient-woodland",
                name="Ancient woodland",
                plural="Ancient woodlands",
                typology="geography",
            )
        ]
        mock_template_response = Mock()
        mock_templates.TemplateResponse.return_value = mock_template_response

        # Execute
        result = get_map(
            mock_request, mock_session, mock_redis, search_query, search_type
        )

        # Assert
        mock_templates.TemplateResponse.assert_called_once_with(
            "national-map.html",
            {
                "request": mock_request,
                "layers": IsListOfDicts(),
                "settings": mock_settings,
                "search_query": "",
                "search_result": None,
                "error": "Enter a postcode",
                "entity_paint_options": None,
                "feedback_form_footer": True,
            },
        )
        assert result == mock_template_response
