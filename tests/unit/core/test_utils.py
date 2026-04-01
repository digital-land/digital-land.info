import time
import pytest

from application.core.utils import (
    entity_attribute_sort_key,
    make_pagination_query_str,
    log_slow_execution,
    map_entity_quality_to_description,
)


quality_test_data = [
    (
        {"quality": "authoritative", "name": "Brownfield site"},
        "Authoritative: We have some data from the authoritative source",
    ),
    (
        {"quality": "some", "name": "Historical monument"},
        "Some: We have some data from an alternative source",
    ),
    (
        {"quality": "trustworthy", "name": "Historic England"},
        "Trustworthy: We have authorititive data linked to material information",
    ),
    (
        {"quality": "usable", "name": "Green space"},
        "Usable: We have data from the authoritative source",
    ),
]


def test_entity_attribute_sort_key_only_excepts_string():
    integer = 10
    try:
        entity_attribute_sort_key(integer)
        assert False
    except ValueError:
        assert True


def test_make_pagination_query_str_preserves_repeated_key_params_when_adding_limit_or_offset():
    query_string_several_datasets = (
        "dataset=ancient-woodland&dataset=battlefield&dataset=conservation-area"
    )

    limit = 10
    offset = 0

    expected = f"{query_string_several_datasets}&limit={limit}"
    result = make_pagination_query_str(query_string_several_datasets, limit, offset)

    assert expected == result

    limit = 10
    offset = 20

    expected = f"{query_string_several_datasets}&limit={limit}&offset={offset}"
    result = make_pagination_query_str(query_string_several_datasets, limit, offset)

    assert expected == result


@log_slow_execution(threshold_seconds=0.5)
def fast_execution():
    time.sleep(0.1)
    return "fast_result"


@log_slow_execution(threshold_seconds=0.5)
def slow_execution():
    time.sleep(0.6)
    return "slow_result"


@log_slow_execution(threshold_seconds=0.5)
def error_fast_function():
    """Function that raises error quickly"""
    time.sleep(0.1)
    raise ValueError("Quick error")


class TestLogSlowExecution:
    def test_fast_execution_does_not_log(self, mocker):
        """
        Tests when `fast_execution()` is called successfully under the
        threshold time neither the info or error logging is triggered.
        """
        mock_logger = mocker.patch("application.core.utils.logger")
        result = fast_execution()

        assert result == "fast_result"
        mock_logger.info.assert_not_called()
        mock_logger.error.assert_not_called()

    def test_slow_execution_logs_execution_time(self, mocker):
        """
        Tests when slow_execution() is called successfully but it's slow and
        the execution time is above the specified threshold, the
        info logging is triggered.
        """
        mock_logger = mocker.patch("application.core.utils.logger")
        result = slow_execution()

        assert result == "slow_result"
        mock_logger.info.assert_called_once()

        call_args = mock_logger.info.call_args
        assert "slow_execution" in call_args[0][0]
        assert "SLOW execution" in call_args[0][0]
        assert "elapsed_seconds" in call_args[1]["extra"]
        assert call_args[1]["extra"]["elapsed_seconds"] >= 0.6
        assert call_args[1]["extra"]["function"] == "slow_execution"

    def test_error_execution_does_log(self, mocker):
        """
        Tests when `error_execution()` raises an exception within
        the threshold time, only an exception error is logged.
        """
        mock_logger = mocker.patch("application.core.utils.logger")
        with pytest.raises(ValueError, match="Quick error"):
            error_fast_function()

        mock_logger.info.assert_not_called()
        mock_logger.error.assert_called()


class TestEntityQualityMapsToDescription:
    @pytest.mark.parametrize("entity_dict, expected", quality_test_data)
    def test_entity_quality_maps_to_description_successfully(entity_dict, expected):
        """Tests mapping the quality field value to the right description."""
        result = map_entity_quality_to_description(entity_dict)
        assert result["quality"] == expected


    def test_entity_quality_maps_to_description_with_empty_quality():
        """Tests function when the quality value is `None`."""
        entity_dict = {"quality": None, "name": "Test Entity"}
        result = map_entity_quality_to_description(entity_dict)
        assert result["quality"] == "We have no data"


    def test_entity_quality_maps_to_description_with_unknown_quality():
        """Tests mapping fails, falls back gracefully."""
        entity_dict = {"quality": "special quality", "name": "Test Entity"}
        result = map_entity_quality_to_description(entity_dict)

        # Should title case the quality even if description not found
        assert result["quality"] == "Special quality"
