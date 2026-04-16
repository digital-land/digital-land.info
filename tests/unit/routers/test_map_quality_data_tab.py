import pytest
from unittest.mock import Mock, patch

from application.routers.map_ import get_quality_colour, get_map
from application.core.models import DatasetModel
from application.core.utils import ENTITY_QUALITY_DESCRIPTION


class TestGetQualityColour:
    """Test cases for the `get_quality_colour` function."""

    def test_get_quality_colour_authoritative(self):
        """Tests that 'authoritative' quality returns the correct colour."""
        result = get_quality_colour("authoritative")
        assert result == "#CCE2D8"

    def test_get_quality_colour_some(self):
        """Tests that 'some' quality returns the correct colour."""
        result = get_quality_colour("some")
        assert result == "#FFF7BF"

    def test_get_quality_colour_usable(self):
        """Tests that 'usable' quality returns the correct colour."""
        result = get_quality_colour("usable")
        assert result == "#817D0D"

    def test_get_quality_colour_trustworthy(self):
        """Tests that 'trustworthy' quality returns the correct colour."""
        result = get_quality_colour("trustworthy")
        assert result == "#3ffd00"

    def test_get_quality_colour_unknown_quality(self):
        """
        Tests that if `quality` has an unknown value, it returns the default
        orange colour.
        """
        result = get_quality_colour("unknown_quality")
        assert result == "#FCD6C3"

    def test_get_quality_colour_empty_string(self):
        """Tests that empty string returns the default orange colour."""
        result = get_quality_colour("")
        assert result == "#FCD6C3"

    def test_get_quality_colour_none(self):
        """
        Tests that if `quality` is None, it returns the default
        orange colour.
        """
        result = get_quality_colour(None)
        assert result == "#FCD6C3"


class TestDataQualityLayerGeneration:
    """Test cases for data quality layer generation in `get_map` function."""

    @pytest.fixture
    def mock_datasets(self):
        """Create mock datasets with different names."""
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
    def mock_quality_map(self):
        """Mock quality values for datasets with mixed scenarios."""
        return {
            "ancient-woodland": ["authoritative", "some"],
            "conservation-area": ["usable", None],  # Mix of real and None values
        }

    @patch("application.routers.map_.get_settings")
    @patch("application.routers.map_.get_datasets_with_data_by_geography")
    @patch("application.routers.map_.get_dataset_quality_values")
    @patch("application.routers.map_.templates")
    def test_data_quality_info_generation(
        self,
        mock_templates,
        mock_get_quality_values,
        mock_get_datasets,
        mock_get_settings,
        mock_datasets,
        mock_quality_map,
    ):
        """Tests that data quality info is properly generated for datasets."""

        # Setup
        mock_request = Mock()
        mock_request.query_params = {}
        mock_session = Mock()
        mock_redis = Mock()
        mock_settings = Mock()

        mock_get_settings.return_value = mock_settings
        mock_get_datasets.return_value = mock_datasets
        mock_get_quality_values.return_value = mock_quality_map

        mock_template_response = Mock()
        mock_templates.TemplateResponse.return_value = mock_template_response

        # Execute
        result = get_map(
            mock_request,
            mock_session,
            mock_redis,
            search_query=None,
            search_type=None,
        )

        call_args = mock_templates.TemplateResponse.call_args
        context = call_args[0][1]

        # Assert
        assert "data_quality_info" in context
        # Should generate 4 quality layers total (ancient-woodland: 2, conservation-area: 2)
        # Including one None quality layer with default description
        assert len(context["data_quality_info"]) == 4

        none_quality_layers = [
            layer for layer in context["data_quality_info"] if layer["quality"] is None
        ]
        assert len(none_quality_layers) == 1
        assert none_quality_layers[0]["description"] == "We have no data"
        assert "We have no data" in none_quality_layers[0]["name"]

        assert result == mock_template_response

    @patch("application.routers.map_.get_settings")
    @patch("application.routers.map_.get_datasets_with_data_by_geography")
    @patch("application.routers.map_.get_dataset_quality_values")
    @patch("application.routers.map_.templates")
    def test_quality_layer_structure(
        self,
        mock_templates,
        mock_get_quality_values,
        mock_get_datasets,
        mock_get_settings,
    ):
        """
        Tests the structure of the quality layer so that it can be used
        by the frontend to display the quality info for datasets.
        """

        # Setup
        mock_datasets = [
            DatasetModel(
                collection="test-dataset",
                dataset="test-dataset",
                name="Test Dataset",
                plural="Test Datasets",
                typology="geography",
            )
        ]

        mock_quality_map = {"test-dataset": ["authoritative"]}
        mock_request = Mock()
        mock_request.query_params = {}
        mock_session = Mock()
        mock_redis = Mock()
        mock_settings = Mock()

        mock_get_settings.return_value = mock_settings
        mock_get_datasets.return_value = mock_datasets
        mock_get_quality_values.return_value = mock_quality_map

        mock_template_response = Mock()
        mock_templates.TemplateResponse.return_value = mock_template_response

        # Execute
        result = get_map(
            mock_request,
            mock_session,
            mock_redis,
            search_query=None,
            search_type=None,
        )

        # Extract data_quality_info
        call_args = mock_templates.TemplateResponse.call_args
        context = call_args[0][1]
        data_quality_info = context["data_quality_info"]

        # Assert
        assert len(data_quality_info) == 1
        quality_layer = data_quality_info[0]

        assert quality_layer["dataset"] == "test-dataset-authoritative"
        assert (
            quality_layer["name"]
            == f"Test Dataset - {ENTITY_QUALITY_DESCRIPTION['authoritative']}"
        )
        assert quality_layer["source_dataset"] == "test-dataset"
        assert quality_layer["quality"] == "authoritative"
        assert result == mock_template_response
