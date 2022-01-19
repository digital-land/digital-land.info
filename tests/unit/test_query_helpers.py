import operator
from datetime import date

import pytest

from application.db.models import EntityOrm
from application.search.enum import DateOption


date_to_filter_params = [
    (
        date(year=2022, month=1, day=1),
        "entry_date",
        {"entry_date_year": 2022, "entry_date_month": 1, "entry_date_day": 1},
    ),
    (
        date(year=2022, month=6, day=10),
        "start_date",
        {"start_date_year": 2022, "start_date_month": 6, "start_date_day": 10},
    ),
    (
        date(year=2022, month=12, day=30),
        "end_date",
        {"end_date_year": 2022, "end_date_month": 12, "end_date_day": 30},
    ),
    (None, "entry_date", {}),
    (None, "entry_date", {"end_date_month": 1, "end_date_day": 1}),
    (
        None,
        "entry_date",
        {"end_date_year": 2022, "end_date_month": 13, "end_date_day": 30},
    ),
    (
        None,
        "entry_date",
        {"end_date_year": 2022, "end_date_month": 1, "end_date_day": 60},
    ),
    (
        None,
        "entry_date",
        {"end_date_year": 2022, "end_date_month": -1, "end_date_day": -30},
    ),
]


@pytest.mark.parametrize("expected, date_field, params", date_to_filter_params)
def test_get_date_to_filter(expected, date_field, params):
    from application.data_access.entity_query_helpers import get_date_to_filter

    assert expected == get_date_to_filter(date_field=date_field, params=params)


date_field_to_filter_params = [
    (EntityOrm.start_date, "start_date"),
    (EntityOrm.end_date, "end_date"),
    (EntityOrm.entry_date, "entry_date"),
    (None, "no_match"),
]


@pytest.mark.parametrize("expected, date_field_name", date_field_to_filter_params)
def test_get_get_date_field_to_filter(expected, date_field_name):
    from application.data_access.entity_query_helpers import get_date_field_to_filter

    assert expected == get_date_field_to_filter(date_field_name)


operator_params = [
    (operator.eq, {}),
    (operator.lt, {"entry_date_match": DateOption.before}),
    (operator.gt, {"entry_date_match": DateOption.since}),
]


@pytest.mark.parametrize("expected, params", operator_params)
def test_get_operator(expected, params):
    from application.data_access.entity_query_helpers import get_operator

    assert expected == get_operator(params)
