from datetime import datetime
import pytest
from sqlalchemy.orm import Query
from application.data_access.entity_queries import _apply_limit_and_pagination_filters
from application.data_access.entity_queries import _apply_period_option_filter
from application.db.models import EntityOrm


def test__apply_limit_and_pagination_filters_with_no_filters_applied():
    query = Query(EntityOrm)
    result = _apply_limit_and_pagination_filters(query, params={"dataset": "testing"})
    assert result._limit_clause is None


@pytest.mark.parametrize(
    "period, end_date",
    [
        (["current"], "2024-12-12"),  # Test case for current entities
        (["historical"], "2023-01-01"),  # Past date for historical entities
        (["all"], None),  # Test case for no filter
    ],
)
def test_apply_period_option_filter(db_session, period, end_date):
    # Create an example entity
    entity = {
        "entry_date": "2024-10-07",
        "start_date": "2020-01-13",
        "end_date": end_date,
        "entity": 2300104,
        "name": "Cooling Towers at the former Willington Power Station",
        "dataset": "certificate-of-immunity",
        "typology": "geography",
        "reference": "1456996",
        "prefix": "certificate-of-immunity",
        "organisation_entity": "16",
        "geometry": "MultiPolygon (((-0.3386878967285156 53.74426323597749, -0.337904691696167 53.743857158459996, -0.33673524856567383 53.744003093019586, -0.33637046813964844 53.74463124033804, -0.3365743160247803 53.74525937826645, -0.33737897872924805 53.74541799747043, -0.33875226974487305 53.74505000000031, -0.3386878967285156 53.74426323597749)))",  # noqa: E501
        "point": "POINT (-0.33737897872924805 53.74541799747043)",
    }

    db_session.add(EntityOrm(**entity))
    db_session.flush()
    query = db_session.query(EntityOrm)

    result = _apply_period_option_filter(query, {"period": period}).all()

    # Check if any result is returned
    assert len(result) > 0
    if period == ["current"]:
        assert all(
            entity.end_date is None or entity.end_date > datetime.now().date()
            for entity in result
        )
    elif period == ["historical"]:
        assert all(entity.end_date < datetime.now().date() for entity in result)
    elif period == ["all"]:
        pass
