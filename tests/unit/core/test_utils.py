import time
import pytest

from unittest.mock import patch

from application.core.utils import (
    entity_attribute_sort_key,
    make_pagination_query_str,
    log_slow_execution,
)


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
def fast_function():
    time.sleep(0.1)
    return "fast_result"


@log_slow_execution(threshold_seconds=0.5)
def slow_function():
    time.sleep(0.6)
    return "slow_result"


@log_slow_execution(threshold_seconds=0.5)
def error_fast_function():
    """Function that raises error quickly"""
    time.sleep(0.1)
    raise ValueError("Quick error")


@log_slow_execution(threshold_seconds=0.5)
def error_slow_function():
    """Function that raises error slowly"""
    time.sleep(0.6)
    raise ValueError("Slow error")


class TestLogSlowExecution:
    @patch("application.core.utils.logger")
    def test_fast_function_does_not_log(self, mock_logger):
        """
        Tests when `fast_function()` is called successfully under the
        threshold time neither the info or error logging is triggered.
        """
        result = fast_function()

        assert result == "fast_result"
        mock_logger.info.assert_not_called()
        mock_logger.error.assert_not_called()

    @patch("application.core.utils.logger")
    def test_slow_function_logs_execution_time(self, mock_logger):
        """
        Tests when `fast_function()` is called successfully but its slow and
        the threshold time is above what is specified the
        info logging is triggered.
        """
        result = slow_function()

        assert result == "slow_result"
        mock_logger.info.assert_called_once()

        call_args = mock_logger.info.call_args
        assert "slow_function" in call_args[0][0]
        assert "SLOW execution" in call_args[0][0]
        assert "elapsed_seconds" in call_args[1]["extra"]
        assert call_args[1]["extra"]["elapsed_seconds"] >= 0.6
        assert call_args[1]["extra"]["function"] == "slow_function"

    @patch("application.core.utils.logger")
    def test_fast_error_does_not_log(self, mock_logger):
        """
        Tests when `error_fast_function()` raises an error but within the
        threshold time, neither info or error logging is not triggered.
        """
        with pytest.raises(ValueError, match="Quick error"):
            error_fast_function()

        mock_logger.info.assert_not_called()
        mock_logger.error.assert_not_called()

    @patch("application.core.utils.logger")
    def test_slow_error_logs_execution_time(self, mock_logger):
        """
        Tests when `error_fast_function()` raises a slow error outside the
        threshold time, error logging is triggered.
        """
        with pytest.raises(ValueError, match="Slow error"):
            error_slow_function()

        mock_logger.error.assert_called_once()

        call_args = mock_logger.error.call_args
        assert "error_slow_function" in call_args[0][0]
        assert "Error in" in call_args[0][0]
        assert "elapsed_seconds" in call_args[1]["extra"]
        assert call_args[1]["extra"]["elapsed_seconds"] >= 0.6
        assert call_args[1]["extra"]["function"] == "error_slow_function"
        assert call_args[1]["exc_info"] is True
