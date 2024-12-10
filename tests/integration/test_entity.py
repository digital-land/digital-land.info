from application.routers.entity import fetch_linked_local_plans
from application.core.models import EntityModel
from application.db.models import EntityOrm


def test_fetch_linked_local_plans(db_session):
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
        "json": {
            "event-date": "2018-11-20",
            "local-plan": "1481207",
            "local-plan-event": "plan-published",
        },
        "organisation_entity": 123,
        "prefix": "local-plan-timetable",
        "reference": "test-timetable",
        "typology": "timetable",
    }
    lpd_entity1 = {
        "entity": 4220004,
        "name": "Local-plan-timetable test1",
        "entry_date": "2019-01-07",
        "start_date": "2019-01-05",
        "end_date": "2020-01-07",
        "dataset": "local-plan-timetable",
        "json": {
            "event-date": "2018-11-20",
            "local-plan": "1481207",
            "local-plan-event": "estimated-plan-published",
        },
        "organisation_entity": 123,
        "prefix": "local-plan-timetable",
        "reference": "test-timetable1",
        "typology": "timetable",
    }
    lpe_entity = {
        "entity": 2950000,
        "reference": "plan-published",
        "name": "Plan published",
        "entry_date": "2019-01-07",
        "start_date": "2019-01-05",
        "end_date": "2020-01-07",
        "dataset": "local-plan-event",
        "organisation_entity": 123,
        "prefix": "local-plan-event",
        "typology": "category",
    }
    lpe_entity1 = {
        "entity": 2950001,
        "reference": "estimated-plan-published",
        "name": "Estimated Plan published",
        "entry_date": "2019-01-07",
        "start_date": "2019-01-05",
        "end_date": "2020-01-07",
        "dataset": "local-plan-event",
        "organisation_entity": 123,
        "prefix": "local-plan-event",
        "typology": "category",
    }

    db_session.add(EntityOrm(**lp_entity))
    db_session.add(EntityOrm(**lpd_entity))
    db_session.add(EntityOrm(**lpd_entity1))
    db_session.add(EntityOrm(**lpe_entity))
    db_session.add(EntityOrm(**lpe_entity1))

    params = {
        "reference": "1481207",
        "name": "Local-plan test",
        "dataset": "local-plan",
        "entity": 4220006,
    }

    linked_entities, boundary = fetch_linked_local_plans(db_session, params)

    assert "local-plan-timetable" in linked_entities
    # Fetch the timetable entities
    timetable_entities = linked_entities["local-plan-timetable"]

    # Ensure timetable_entities is a list
    assert isinstance(
        timetable_entities, list
    ), "Expected timetable_entities to be a list"

    # Ensure at least one timetable entity exists
    assert len(timetable_entities) == 2, "Expected 2 timetable entity in 'local-plan'"
    assert isinstance(timetable_entities[0].local_plan_event, EntityModel)
    assert timetable_entities[1].local_plan_event is None
    # Since it is estimated, it should not come in the list
    assert timetable_entities[0].local_plan_event.name == "Plan published"
