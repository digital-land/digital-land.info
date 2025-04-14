from datetime import datetime
import pytest
from application.data_access.entity_queries import get_organisations, lookup_entity_link
from application.data_access.entity_queries import (
    _apply_period_option_filter,
    get_linked_entities,
)
from application.db.models import EntityOrm


def test__lookup_entity_link_returns_nothing_when_the_entity_isnt_found(db_session):
    linked_entity = lookup_entity_link(
        db_session, "a-reference", "article-4-direction", 123
    )
    assert linked_entity is None


def test__lookup_entity_link_returns_the_looked_up_entity_when_the_link_exists(
    db_session,
):
    lookup_entity = {
        "entity": 106,
        "name": "A space",
        "entry_date": "2019-01-07",
        "start_date": "2019-01-05",
        "end_date": "2020-01-07",
        "dataset": "article-4-direction",
        "json": None,
        "organisation_entity": 123,
        "prefix": "greenspace",
        "reference": "a-reference",
        "typology": "geography",
        "geometry": "MultiPolygon (((-0.3386878967285156 53.74426323597749, -0.337904691696167 53.743857158459996, -0.33673524856567383 53.744003093019586, -0.33637046813964844 53.74463124033804, -0.3365743160247803 53.74525937826645, -0.33737897872924805 53.74541799747043, -0.33875226974487305 53.74505000000031, -0.3386878967285156 53.74426323597749)))",  # noqa: E501
        "point": "POINT (-0.33737897872924805 53.74541799747043)",
    }

    db_session.add(EntityOrm(**lookup_entity))

    linked_entity = lookup_entity_link(
        db_session, "a-reference", "article-4-direction", 123
    )
    assert linked_entity["entity"] == lookup_entity["entity"]
    assert linked_entity["reference"] == lookup_entity["reference"]
    assert linked_entity["dataset"] == lookup_entity["dataset"]
    assert linked_entity["typology"] == lookup_entity["typology"]
    assert linked_entity["name"] == lookup_entity["name"]
    assert linked_entity["reference"] == lookup_entity["reference"]


def test__lookup_entity_link_returns_entity_without_organisation_entity(db_session):
    lookup_entity = {
        "entity": 106,
        "reference": "a-reference",
        "dataset": "article-4-direction",
        "organisation_entity": 123,
        "name": "A space",
    }
    db_session.add(EntityOrm(**lookup_entity))
    linked_entity = lookup_entity_link(db_session, "a-reference", "article-4-direction")

    assert linked_entity["entity"] == lookup_entity["entity"]
    assert linked_entity["reference"] == lookup_entity["reference"]
    assert linked_entity["dataset"] == lookup_entity["dataset"]


@pytest.mark.parametrize("period", [["current"], ["historical"], ["all"]])
def test_apply_period_option_filter(db_session, period):
    entities = [
        {
            "entry_date": "2024-10-07",
            "start_date": "2020-01-13",
            "end_date": "2023-01-12",
            "entity": 2300104,
            "name": "Cooling Towers at the former Willington Power Station",
            "dataset": "certificate-of-immunity",
            "typology": "geography",
            "reference": "1456996",
            "prefix": "certificate-of-immunity",
            "organisation_entity": "16",
            "geometry": "MultiPolygon (((-0.3386878967285156 53.74426323597749, -0.337904691696167 53.743857158459996, -0.33673524856567383 53.744003093019586, -0.33637046813964844 53.74463124033804, -0.3365743160247803 53.74525937826645, -0.33737897872924805 53.74541799747043, -0.33875226974487305 53.74505000000031, -0.3386878967285156 53.74426323597749)))",  # noqa: E501
            "point": "POINT (-0.33737897872924805 53.74541799747043)",
        },
        {
            "entry_date": "2024-10-07",
            "start_date": "2020-01-13",
            "end_date": "2000-01-12",
            "entity": 2300103,
            "name": "Cooling Towers at the former Willington Power Station",
            "dataset": "certificate-of-immunity",
            "typology": "geography",
            "reference": "1456995",
            "prefix": "certificate-of-immunity",
            "organisation_entity": "16",
            "geometry": "MultiPolygon (((-0.3386878967285156 53.74426323597749, -0.337904691696167 53.743857158459996, -0.33673524856567383 53.744003093019586, -0.33637046813964844 53.74463124033804, -0.3365743160247803 53.74525937826645, -0.33737897872924805 53.74541799747043, -0.33875226974487305 53.74505000000031, -0.3386878967285156 53.74426323597749)))",  # noqa: E501
            "point": "POINT (-0.33737897872924805 53.74541799747043)",
        },
        {
            "entry_date": "2024-10-07",
            "start_date": "2020-01-13",
            "end_date": "2030-12-12",
            "entity": 2300106,
            "name": "Cooling Towers at the former Willington Power Station",
            "dataset": "certificate-of-immunity",
            "typology": "geography",
            "reference": "1456997",
            "prefix": "certificate-of-immunity",
            "organisation_entity": "16",
            "geometry": "MultiPolygon (((-0.3386878967285156 53.74426323597749, -0.337904691696167 53.743857158459996, -0.33673524856567383 53.744003093019586, -0.33637046813964844 53.74463124033804, -0.3365743160247803 53.74525937826645, -0.33737897872924805 53.74541799747043, -0.33875226974487305 53.74505000000031, -0.3386878967285156 53.74426323597749)))",  # noqa: E501
            "point": "POINT (-0.33737897872924805 53.74541799747043)",
        },
        {
            "entry_date": "2024-10-07",
            "start_date": "2020-01-13",
            "end_date": "2050-01-12",
            "entity": 2300105,
            "name": "Cooling Towers at the former Willington Power Station",
            "dataset": "certificate-of-immunity",
            "typology": "geography",
            "reference": "1456999",
            "prefix": "certificate-of-immunity",
            "organisation_entity": "16",
            "geometry": "MultiPolygon (((-0.3386878967285156 53.74426323597749, -0.337904691696167 53.743857158459996, -0.33673524856567383 53.744003093019586, -0.33637046813964844 53.74463124033804, -0.3365743160247803 53.74525937826645, -0.33737897872924805 53.74541799747043, -0.33875226974487305 53.74505000000031, -0.3386878967285156 53.74426323597749)))",  # noqa: E501
            "point": "POINT (-0.33737897872924805 53.74541799747043)",
        },
    ]
    for entity in entities:
        db_session.add(EntityOrm(**entity))

    db_session.flush()
    query = db_session.query(EntityOrm)
    result = _apply_period_option_filter(query, {"period": period}).all()

    if period == ["current"]:
        assert all(
            entity.end_date is None or entity.end_date > datetime.now().date()
            for entity in result
        )
    if period == ["historical"]:
        assert all(entity.end_date < datetime.now().date() for entity in result)
    if period == ["all"]:
        assert len(result) == 4


def test__local_plan_linked_entity_timetable(
    db_session,
):
    lp_entity = {
        "entity": 4220006,
        "name": "Local-plan test",
        "entry_date": "2019-01-07",
        "start_date": "2019-01-05",
        "end_date": "2020-01-07",
        "dataset": "local-plan",
        "json": {
            "adopted-date": "2018-09-27",
            "documentation-url": "https://www.scambs.gov.uk/planning/south-cambridgeshire-local-plan-2018",
            "local-plan-boundary": "E07000012",
        },
        "organisation_entity": 123,
        "prefix": "local-plan",
        "reference": "1481207",
        "typology": "legal-instrument",
    }

    lpd_entity = {
        "entity": 4220005,
        "name": "Local-plan-timetable test",
        "entry_date": "2019-01-07",
        "start_date": "2019-01-05",
        "end_date": "2020-01-07",
        "dataset": "local-plan-timetable",
        "json": {"event-date": "2018-11-20", "local-plan": "1481207"},
        "organisation_entity": 123,
        "prefix": "local-plan-timetable",
        "reference": "test-timetable",
        "typology": "timetable",
    }
    lpd_entity1 = {
        "entity": 4220004,
        "name": "Local-plan-document test",
        "entry_date": "2019-01-07",
        "start_date": "2019-01-05",
        "end_date": "2020-01-07",
        "dataset": "local-plan-document",
        "json": {"event-date": "2018-11-20", "local-plan": "1481207"},
        "organisation_entity": 123,
        "prefix": "local-plan-document",
        "reference": "test-document",
        "typology": "document",
    }

    db_session.add(EntityOrm(**lp_entity))
    db_session.add(EntityOrm(**lpd_entity))
    db_session.add(EntityOrm(**lpd_entity1))

    linked_entities = get_linked_entities(
        db_session, "local-plan-timetable", "1481207", "local-plan"
    )

    # Assert the linked entity has reference 'test-document'
    assert isinstance(linked_entities, list), "Expected linked_entities to be a list"
    assert len(linked_entities) == 1, "Expected at least one linked entity"
    assert linked_entities[0].reference == "test-timetable"


def test__local_plan_linked_entity_timetable_order_check(
    db_session,
):
    lp_entity = {
        "entity": 4220006,
        "name": "Local-plan test",
        "entry_date": "2019-01-07",
        "start_date": "2019-01-05",
        "end_date": "2020-01-07",
        "dataset": "local-plan",
        "json": {
            "adopted-date": "2018-09-27",
            "documentation-url": "https://www.scambs.gov.uk/planning/south-cambridgeshire-local-plan-2018",
            "local-plan-boundary": "E07000012",
        },
        "organisation_entity": 123,
        "prefix": "local-plan",
        "reference": "1481207",
        "typology": "legal-instrument",
    }

    lpd_entity = {
        "entity": 4220005,
        "name": "Local-plan-document test",
        "entry_date": "2019-01-07",
        "start_date": "2019-01-05",
        "end_date": "2020-01-07",
        "dataset": "local-plan-timetable",
        "json": {"event-date": "2018-11-20", "local-plan": "1481207"},
        "organisation_entity": 123,
        "prefix": "local-plan-document",
        "reference": "test-document",
        "typology": "document",
    }
    lpd_entity1 = {
        "entity": 4220004,
        "name": "Local-plan-document test",
        "entry_date": "2019-01-07",
        "start_date": "2019-01-05",
        "end_date": "2020-01-07",
        "dataset": "local-plan-timetable",
        "json": {"event-date": "2022-11-20", "local-plan": "1481207"},
        "organisation_entity": 123,
        "prefix": "local-plan-document",
        "reference": "test-document",
        "typology": "document",
    }

    db_session.add(EntityOrm(**lp_entity))
    db_session.add(EntityOrm(**lpd_entity))
    db_session.add(EntityOrm(**lpd_entity1))

    linked_entities = get_linked_entities(
        db_session, "local-plan-timetable", "1481207", "local-plan"
    )

    # Assert the linked entity has reference 'test-document'
    assert isinstance(linked_entities, list), "Expected linked_entities to be a list"
    assert len(linked_entities) == 2, "Expected at least one linked entity"
    assert linked_entities[0].event_date == "2022-11-20"


@pytest.mark.parametrize(
    "organisation_entity",
    [
        {
            "entity": 4220006,
            "name": "Organisation A",
            "entry_date": "2019-01-07",
            "start_date": "2019-01-05",
            "end_date": "2020-01-07",
            "dataset": "organisation-dataset",
            "json": {},
            "organisation_entity": "600002",
            "prefix": "organisation",
            "reference": "1481207",
            "typology": "organisation",
        },
        {
            "entity": 4220006,
            "name": None,
            "entry_date": "2019-01-07",
            "start_date": "2019-01-05",
            "end_date": "2020-01-07",
            "dataset": "organisation-dataset",
            "json": {},
            "organisation_entity": None,
            "prefix": "organisation",
            "reference": "1481207",
            "typology": "organisation",
        },
    ],
)
def test_get_organisations(db_session, organisation_entity):
    db_session.add(EntityOrm(**organisation_entity))
    db_session.commit()

    organisations = get_organisations(db_session)
    if organisation_entity["name"]:
        assert (
            organisations[0].name == organisation_entity["name"]
        ), f"Expected organisation name '{organisation_entity['name']}'"
    else:
        assert (
            organisations == []
        ), "Expected no organisations to be returned when name is None"
