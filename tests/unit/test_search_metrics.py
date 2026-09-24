from unittest.mock import Mock, patch

import pytest

from application.core.search_metrics import measure_entity_search
from application.search.enum import SuffixEntity


def test_search_duration_preserves_result_and_parameters():
    search = Mock(return_value={"count": 2, "entities": []})
    params = {"geometry_curie": ["statistical-geography:B", "statistical-geography:A"]}
    session = object()
    with (
        patch("application.core.search_metrics.perf_counter", side_effect=[10, 12.5]),
        patch(
            "application.core.search_metrics.sentry_sdk.metrics.distribution"
        ) as metric,
    ):
        result = measure_entity_search(search)(session, params, SuffixEntity.json)

    assert result is search.return_value
    search.assert_called_once_with(session, params, SuffixEntity.json)
    assert params["geometry_curie"][0] == "statistical-geography:B"
    assert metric.call_args.args == ("entity.search.duration", 2500)
    assert metric.call_args.kwargs["unit"] == "millisecond"
    attributes = metric.call_args.kwargs["attributes"]
    assert attributes["outcome"] == "success"
    assert attributes["extension"] == "json"
    assert attributes["search.geometry_curie"] == (
        "statistical-geography:A,statistical-geography:B"
    )


def test_search_group_is_stable_but_distinguishes_different_requests():
    search = measure_entity_search(Mock(return_value={}))
    with patch(
        "application.core.search_metrics.sentry_sdk.metrics.distribution"
    ) as metric:
        search(None, {"geometry_curie": ["b", "a"], "limit": 100})
        search(None, {"limit": 100, "geometry_curie": ["a", "b"], "dataset": None})
        search(None, {"geometry_curie": ["a", "b"], "limit": 10})
        search(None, {"geometry_curie": ["a", "b"], "limit": 100}, SuffixEntity.json)

    groups = [
        call.kwargs["attributes"]["search.group"] for call in metric.call_args_list
    ]
    assert groups[0] == groups[1]
    assert groups[0] != groups[2]
    assert groups[0] != groups[3]


def test_failed_search_records_duration_and_reraises_original_error():
    error = RuntimeError("query timeout")
    search = measure_entity_search(Mock(side_effect=error))
    with (
        patch("application.core.search_metrics.perf_counter", side_effect=[10, 70]),
        patch(
            "application.core.search_metrics.sentry_sdk.metrics.distribution"
        ) as metric,
        pytest.raises(RuntimeError) as raised,
    ):
        search(None, {})

    assert raised.value is error
    assert metric.call_args.args == ("entity.search.duration", 60000)
    assert metric.call_args.kwargs["attributes"]["outcome"] == "error"


@pytest.mark.parametrize("search_fails", [False, True])
def test_metric_failure_does_not_change_search_outcome(search_fails):
    error = RuntimeError("query timeout")
    result = {"count": 0, "entities": []}
    search = measure_entity_search(
        Mock(return_value=result, side_effect=error if search_fails else None)
    )
    with patch(
        "application.core.search_metrics.sentry_sdk.metrics.distribution",
        side_effect=RuntimeError("metric failure"),
    ):
        if search_fails:
            with pytest.raises(RuntimeError) as raised:
                search(None, {})
            assert raised.value is error
        else:
            assert search(None, {}) is result
