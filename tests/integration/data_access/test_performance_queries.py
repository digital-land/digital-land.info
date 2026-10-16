from datetime import date

from application.db.models import ProvisionQualityOrm
from application.data_access.performance_queries import (
    a_year_before,
    count_authoritative_data_providers,
    count_data_providers,
    count_data_providers_by_year,
    count_datasets,
    get_performance_summary,
)


def add_provision_quality(
    db_session,
    dataset="greenspace",
    organisation="local-authority:X",
    start_date=date(2024, 1, 1),
    quality="authoritative",
    entity_count=10,
):
    db_session.add(
        ProvisionQualityOrm(
            dataset=dataset,
            organisation=organisation,
            organisation_name="Test Council",
            has_active_endpoint=True,
            has_active_resource=True,
            owns_entities=True,
            is_designated_provider=True,
            quality=quality,
            entity_count=entity_count,
            quality_score=None,
            start_date=start_date,
        )
    )


class TestCountDataProviders:
    def test_counts_nothing_when_no_providers(self, db_session):
        assert count_data_providers(db_session, date(2026, 1, 1)) == 0

    def test_counts_an_organisation_that_published_before_the_date(self, db_session):
        add_provision_quality(db_session, start_date=date(2024, 1, 1))
        db_session.flush()

        assert count_data_providers(db_session, date(2026, 1, 1)) == 1

    def test_excludes_an_organisation_that_published_after_the_date(self, db_session):
        add_provision_quality(db_session, start_date=date(2026, 6, 1))
        db_session.flush()

        assert count_data_providers(db_session, date(2026, 1, 1)) == 0

    def test_counts_an_organisation_with_no_start_date_if_it_has_produced_entities(
        self, db_session
    ):
        """
        provision_quality rows can have real entities with no start_date
        recorded at all. Excluding them entirely would undercount the
        total, so they are treated as having been there since the
        earliest possible date - always included in the current count,
        at the cost of never being able to show up as newly added (see
        _started_on_or_before).
        """
        add_provision_quality(db_session, start_date=None)
        db_session.flush()

        assert count_data_providers(db_session, date(2026, 1, 1)) == 1

    def test_excludes_an_organisation_with_no_start_date_and_no_entities(
        self, db_session
    ):
        add_provision_quality(db_session, start_date=None, entity_count=0)
        db_session.flush()

        assert count_data_providers(db_session, date(2026, 1, 1)) == 0

    def test_counts_an_organisation_once_across_several_datasets(self, db_session):
        add_provision_quality(db_session, dataset="greenspace")
        add_provision_quality(db_session, dataset="conservation-area")
        db_session.flush()

        assert count_data_providers(db_session, date(2026, 1, 1)) == 1

    def test_excludes_a_provider_whose_dataset_never_produced_any_entities(
        self, db_session
    ):
        add_provision_quality(db_session, start_date=date(2024, 1, 1), entity_count=0)
        db_session.flush()

        assert count_data_providers(db_session, date(2026, 1, 1)) == 0


class TestCountDatasets:
    def test_counts_a_dataset_once_across_several_providers(self, db_session):
        add_provision_quality(db_session, organisation="local-authority:X")
        add_provision_quality(db_session, organisation="local-authority:Y")
        db_session.flush()

        assert count_datasets(db_session, date(2026, 1, 1)) == 1

    def test_counts_each_published_dataset(self, db_session):
        add_provision_quality(db_session, dataset="greenspace")
        add_provision_quality(db_session, dataset="conservation-area")
        db_session.flush()

        assert count_datasets(db_session, date(2026, 1, 1)) == 2

    def test_excludes_a_dataset_that_has_never_produced_any_entities(self, db_session):
        add_provision_quality(db_session, entity_count=0)
        db_session.flush()

        assert count_datasets(db_session, date(2026, 1, 1)) == 0

    def test_counts_a_dataset_if_any_provider_has_produced_entities(self, db_session):
        add_provision_quality(
            db_session, organisation="local-authority:X", entity_count=0
        )
        add_provision_quality(
            db_session, organisation="local-authority:Y", entity_count=10
        )
        db_session.flush()

        assert count_datasets(db_session, date(2026, 1, 1)) == 1

    def test_counts_a_dataset_with_no_start_date_if_it_has_produced_entities(
        self, db_session
    ):
        add_provision_quality(db_session, start_date=None)
        db_session.flush()

        assert count_datasets(db_session, date(2026, 1, 1)) == 1


class TestCountAuthoritativeDataProviders:
    def test_counts_nothing_when_no_providers(self, db_session):
        assert count_authoritative_data_providers(db_session, date(2026, 1, 1)) == 0

    def test_counts_a_provider_for_each_authoritative_quality(self, db_session):
        """
        AUTHORITATIVE_QUALITIES is ("authoritative", "usable", "trustworthy") -
        each is checked against its own organisation, in isolation, so a
        regression to any one of the three is caught on its own rather than
        being masked by the other two still passing.
        """
        as_at = date(2026, 1, 1)

        add_provision_quality(
            db_session, organisation="local-authority:A", quality="authoritative"
        )
        db_session.flush()
        assert count_authoritative_data_providers(db_session, as_at) == 1

        add_provision_quality(
            db_session, organisation="local-authority:B", quality="usable"
        )
        db_session.flush()
        assert count_authoritative_data_providers(db_session, as_at) == 2

        add_provision_quality(
            db_session, organisation="local-authority:C", quality="trustworthy"
        )
        db_session.flush()
        assert count_authoritative_data_providers(db_session, as_at) == 3

    def test_excludes_a_provider_whose_only_quality_is_not_authoritative(
        self, db_session
    ):
        add_provision_quality(db_session, quality="some")
        db_session.flush()

        assert count_authoritative_data_providers(db_session, date(2026, 1, 1)) == 0

    def test_counts_a_provider_once_even_if_multiple_datasets_are_authoritative(
        self, db_session
    ):
        add_provision_quality(
            db_session,
            organisation="local-authority:X",
            dataset="greenspace",
            quality="authoritative",
        )
        add_provision_quality(
            db_session,
            organisation="local-authority:X",
            dataset="conservation-area",
            quality="trustworthy",
        )
        db_session.flush()

        assert count_authoritative_data_providers(db_session, date(2026, 1, 1)) == 1

    def test_counts_a_provider_that_is_authoritative_for_only_one_of_its_datasets(
        self, db_session
    ):
        """
        A provider is authoritative overall if any of its provision meets
        the bar - the same rule the data providers page uses per dataset,
        applied across all of a provider's datasets.
        """
        add_provision_quality(
            db_session,
            organisation="local-authority:X",
            dataset="greenspace",
            quality="some",
        )
        add_provision_quality(
            db_session,
            organisation="local-authority:X",
            dataset="conservation-area",
            quality="authoritative",
        )
        db_session.flush()

        assert count_authoritative_data_providers(db_session, date(2026, 1, 1)) == 1

    def test_is_never_more_than_the_total_number_of_providers(self, db_session):
        add_provision_quality(
            db_session, organisation="local-authority:X", quality="authoritative"
        )
        add_provision_quality(
            db_session, organisation="local-authority:Y", quality="some"
        )
        db_session.flush()

        as_at = date(2026, 1, 1)
        assert count_authoritative_data_providers(db_session, as_at) == 1
        assert count_data_providers(db_session, as_at) == 2


class TestGetPerformanceSummary:
    def test_assembles_counts_and_changes_for_both_metrics(self, db_session):
        today = date.today()
        add_provision_quality(
            db_session,
            dataset="greenspace",
            organisation="local-authority:X",
            start_date=a_year_before(a_year_before(a_year_before(today))),
            quality="authoritative",
        )
        add_provision_quality(
            db_session,
            dataset="conservation-area",
            organisation="local-authority:Y",
            start_date=today.replace(day=1),
            quality="some",
        )
        db_session.flush()

        summary = get_performance_summary(db_session, today)

        assert summary == {
            "counted_on": today,
            "previously_counted_on": a_year_before(today),
            "dataset_count": 2,
            "dataset_count_change": 1,
            "data_provider_count": 2,
            "data_provider_count_change": 1,
            "authoritative_provider_count": 1,
            "alternative_provider_count": 1,
        }


class TestCountDataProvidersByYear:
    def test_counts_nothing_when_no_providers(self, db_session):
        assert count_data_providers_by_year(db_session, date(2026, 1, 1)) == []

    def test_accumulates_providers_across_years(self, db_session):
        add_provision_quality(
            db_session, organisation="local-authority:X", start_date=date(2024, 3, 1)
        )
        add_provision_quality(
            db_session, organisation="local-authority:Y", start_date=date(2025, 3, 1)
        )
        add_provision_quality(
            db_session, organisation="local-authority:Z", start_date=date(2025, 9, 1)
        )
        db_session.flush()

        assert count_data_providers_by_year(db_session, date(2026, 1, 1)) == [
            {"year": 2024, "running_total": 1},
            {"year": 2025, "running_total": 3},
        ]

    def test_dates_a_provider_by_its_earliest_dataset(self, db_session):
        add_provision_quality(
            db_session, dataset="greenspace", start_date=date(2024, 3, 1)
        )
        add_provision_quality(
            db_session, dataset="conservation-area", start_date=date(2025, 3, 1)
        )
        db_session.flush()

        assert count_data_providers_by_year(db_session, date(2026, 1, 1)) == [
            {"year": 2024, "running_total": 1}
        ]

    def test_excludes_years_after_the_date(self, db_session):
        add_provision_quality(
            db_session, organisation="local-authority:X", start_date=date(2024, 3, 1)
        )
        add_provision_quality(
            db_session, organisation="local-authority:Y", start_date=date(2026, 3, 1)
        )
        db_session.flush()

        assert count_data_providers_by_year(db_session, date(2026, 1, 1)) == [
            {"year": 2024, "running_total": 1}
        ]

    def test_excludes_a_provider_that_has_never_produced_any_entities(self, db_session):
        add_provision_quality(db_session, start_date=date(2024, 3, 1), entity_count=0)
        db_session.flush()

        assert count_data_providers_by_year(db_session, date(2026, 1, 1)) == []

    def test_dates_a_provider_by_its_earliest_dataset_with_real_data(self, db_session):
        """
        The greenspace row is earlier but contains 0 entities - the
        conservation-area row is what actually counts as "first published".
        """
        add_provision_quality(
            db_session,
            dataset="greenspace",
            start_date=date(2023, 1, 1),
            entity_count=0,
        )
        add_provision_quality(
            db_session,
            dataset="conservation-area",
            start_date=date(2024, 3, 1),
            entity_count=10,
        )
        db_session.flush()

        assert count_data_providers_by_year(db_session, date(2026, 1, 1)) == [
            {"year": 2024, "running_total": 1}
        ]

    def test_dates_a_provider_with_no_start_date_to_the_earliest_possible_year(
        self, db_session
    ):
        """
        A provider with no start_date on any of its rows is counted from
        the earliest possible date (see _started_on_or_before) - so it
        appears in year 1, the only year that date.min can ever fall in.
        This applies even when the same provider also has a later, dated
        row: the earliest value always wins once the two are compared.
        """
        add_provision_quality(
            db_session,
            organisation="local-authority:X",
            dataset="greenspace",
            start_date=None,
        )
        add_provision_quality(
            db_session,
            organisation="local-authority:X",
            dataset="conservation-area",
            start_date=date(2024, 3, 1),
        )
        db_session.flush()

        assert count_data_providers_by_year(db_session, date(2026, 1, 1)) == [
            {"year": 1, "running_total": 1}
        ]


class TestAYearBefore:
    def test_subtracts_a_year(self):
        assert a_year_before(date(2026, 10, 2)) == date(2025, 10, 2)

    def test_moves_back_a_day_when_the_year_before_has_no_29_february(self):
        assert a_year_before(date(2024, 2, 29)) == date(2023, 2, 28)
