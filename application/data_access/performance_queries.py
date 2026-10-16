from datetime import date
from typing import List

from sqlalchemy import func
from sqlalchemy.orm import Session

from application.core.models import AUTHORITATIVE_QUALITIES
from application.db.models import ProvisionQualityOrm


def a_year_before(day: date) -> date:
    try:
        return day.replace(year=day.year - 1)
    except ValueError:
        return day.replace(year=day.year - 1, day=day.day - 1)


def _has_real_data():
    """
    A provision_quality row only represents real, available data once it has
    produced at least one entity - a registered endpoint with zero entities
    hasn't given us anything a user could use.
    """
    return (ProvisionQualityOrm.entity_count > 0,)


def _started_on_or_before(as_at: date):
    """
    Many provision_quality rows have no start_date at all, even when they
    have real entities (see _has_real_data).

    Rather than excluding those rows from every count, they are treated as
    having been there since the earliest possible date, so they are always
    included in the current total.

    Accepted cost: a row with no start_date can never show up as newly
    added in a year-on-year comparison, even if it genuinely was added
    recently - there is nothing in provision_quality to tell the two cases
    apart.
    """
    started_on = func.coalesce(ProvisionQualityOrm.start_date, date.min)
    return (started_on <= as_at,)


def _published_data_filters_on_or_before(as_at: date):
    return _has_real_data() + _started_on_or_before(as_at)


def _count_distinct_with_data(session: Session, column, as_at: date) -> int:
    return (
        session.query(func.count(func.distinct(column)))
        .filter(*_published_data_filters_on_or_before(as_at))
        .scalar()
        or 0
    )


def count_data_providers(session: Session, as_at: date) -> int:
    return _count_distinct_with_data(session, ProvisionQualityOrm.organisation, as_at)


def count_datasets(session: Session, as_at: date) -> int:
    return _count_distinct_with_data(session, ProvisionQualityOrm.dataset, as_at)


def count_authoritative_data_providers(session: Session, as_at: date) -> int:
    """
    Of the providers counted by count_data_providers, how many have published
    at least one dataset to an authoritative standard. The remainder -
    count_data_providers(...) minus this - are alternative sources.
    """
    return (
        session.query(func.count(func.distinct(ProvisionQualityOrm.organisation)))
        .filter(*_published_data_filters_on_or_before(as_at))
        .filter(ProvisionQualityOrm.quality.in_(AUTHORITATIVE_QUALITIES))
        .scalar()
        or 0
    )


def count_data_providers_by_year(session: Session, as_at: date) -> List[dict]:
    first_published = (
        session.query(
            func.min(func.coalesce(ProvisionQualityOrm.start_date, date.min)).label(
                "first_published"
            ),
        )
        .filter(*_has_real_data())
        .group_by(ProvisionQualityOrm.organisation)
        .subquery()
    )
    year = func.extract("year", first_published.c.first_published)

    first_published_each_year = (
        session.query(year.label("year"), func.count().label("newly_published"))
        .filter(first_published.c.first_published <= as_at)
        .group_by(year)
        .order_by(year)
        .all()
    )

    running_total = 0
    counts = []
    for row in first_published_each_year:
        running_total += row.newly_published
        counts.append({"year": int(row.year), "running_total": running_total})
    return counts


def get_performance_summary(session: Session, as_at: date) -> dict:
    """
    Data required for the performance page
    """
    previously_counted_on = a_year_before(as_at)

    dataset_count = count_datasets(session, as_at)
    data_provider_count = count_data_providers(session, as_at)
    authoritative_provider_count = count_authoritative_data_providers(session, as_at)

    return {
        "counted_on": as_at,
        "previously_counted_on": previously_counted_on,
        "dataset_count": dataset_count,
        "dataset_count_change": dataset_count
        - count_datasets(session, previously_counted_on),
        "data_provider_count": data_provider_count,
        "data_provider_count_change": data_provider_count
        - count_data_providers(session, previously_counted_on),
        "authoritative_provider_count": authoritative_provider_count,
        "alternative_provider_count": data_provider_count
        - authoritative_provider_count,
    }
