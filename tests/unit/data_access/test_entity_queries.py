import pytest
from sqlalchemy.orm import Query
from application.data_access.entity_queries import _apply_limit_and_pagination_filters
from application.data_access.entity_queries import _apply_period_option_filter
from application.db.models import EntityOrm
from unittest.mock import MagicMock


def test__apply_limit_and_pagination_filters_with_no_filters_applied():
    query = Query(EntityOrm)
    result = _apply_limit_and_pagination_filters(query, params={"dataset": "testing"})
    assert result._limit_clause is None


@pytest.mark.parametrize(
    "period, expected_count, end_date",
    [
        (["current"], 1, None),  # Test case for current entities
        (["historical"], 1, "2023-01-01"),  # Past date for historical entities
        (["all"], 1, None),  # Test case for no filter
    ],
)
def test__apply_period_option_filter(mocker, period, expected_count, end_date):
    mock_get_session = mocker.patch(
        "application.routers.entity.get_session", return_value=MagicMock()
    )
    session = mock_get_session.return_value
    entity = EntityOrm(end_date=end_date)
    mock_query = MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.all.return_value = [entity]
    session.query.return_value = mock_query

    query = session.query(EntityOrm)
    result = _apply_period_option_filter(query, {"period": period}).all()

    assert len(result) == expected_count
    if expected_count > 0:
        assert result[0].end_date == end_date
