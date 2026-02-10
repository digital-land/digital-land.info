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
        "name": "Development-plan-timetable test",
        "entry_date": "2019-01-07",
        "start_date": "2019-01-05",
        "end_date": "2020-01-07",
        "dataset": "development-plan-timetable",
        "json": {
            "event-date": "2018-11-20",
            "local-plan": "1481207",
            "development-plan-event": "plan-published",
        },
        "organisation_entity": 123,
        "prefix": "development-plan-timetable",
        "reference": "test-timetable",
        "typology": "timetable",
    }
    lpd_entity1 = {
        "entity": 4220004,
        "name": "development-plan-timetable test1",
        "entry_date": "2019-01-07",
        "start_date": "2019-01-05",
        "end_date": "2020-01-07",
        "dataset": "development-plan-timetable",
        "json": {
            "event-date": "2018-11-20",
            "local-plan": "1481207",
            "development-plan-event": "estimated-plan-published",
        },
        "organisation_entity": 123,
        "prefix": "development-plan-timetable",
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
        "dataset": "development-plan-event",
        "organisation_entity": 123,
        "prefix": "development-plan-event",
        "typology": "category",
    }
    lpe_entity1 = {
        "entity": 2950001,
        "reference": "estimated-plan-published",
        "name": "Estimated Plan published",
        "entry_date": "2019-01-07",
        "start_date": "2019-01-05",
        "end_date": "2020-01-07",
        "dataset": "development-plan-event",
        "organisation_entity": 123,
        "prefix": "development-plan-event",
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
        "local-plan-boundary": "E07000012",
    }

    linked_entities, boundary = fetch_linked_local_plans(db_session, params)

    assert boundary is None
    assert "development-plan-timetable" in linked_entities
    # Fetch the timetable entities
    timetable_entities = linked_entities["development-plan-timetable"]

    # Ensure timetable_entities is a list
    assert isinstance(
        timetable_entities, list
    ), "Expected timetable_entities to be a list"

    # Ensure at least one timetable entity exists
    assert len(timetable_entities) == 2, "Expected 2 timetable entity in 'local-plan'"
    assert isinstance(timetable_entities[0].development_plan_event, EntityModel)
    assert timetable_entities[1].development_plan_event is None
    # Since it is estimated, it should not come in the list
    assert timetable_entities[0].development_plan_event.name == "Plan published"

    assert "local-plan-housing" in linked_entities
    assert linked_entities["local-plan-housing"] == []

def test_fetch_linked_local_plans_boundary(db_session):
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
    lpb_entity = {
        "entity": 4211000,
        "name": "London Borough of Camden statistical geography",
        "entry_date": "2019-01-07",
        "start_date": "2019-01-05",
        "end_date": "2020-01-07",
        "dataset": "local-plan-boundary",
        "json": {"plan-boundary-type": "statistical-geography"},
        "organisation_entity": 123,
        "prefix": "local-plan-boundary",
        "reference": "E07000012",
        "geometry": "MULTIPOLYGON (((0.145139 50.986737, 0.145088 50.986778, 0.14514 50.986847, 0.145396 50.986967, 0.145637 50.987097, 0.146009 50.987359, 0.146495 50.987534, 0.147003 50.987879, 0.146999 50.98789, 0.146832 50.98782, 0.14675 50.987863, 0.146429 50.98773, 0.146216 50.987625, 0.145928 50.987469, 0.145798 50.987427, 0.145756 50.987446, 0.145731 50.987486, 0.145754 50.987549, 0.145829 50.987668, 0.145894 50.987742, 0.145831 50.98778, 0.145781 50.987713, 0.145405 50.9874, 0.145226 50.987192, 0.145165 50.98715, 0.145051 50.987095, 0.144917 50.986998, 0.144766 50.98692, 0.144581 50.986844, 0.143894 50.98667, 0.144057 50.986489, 0.144149 50.986526, 0.144366 50.986527, 0.144423 50.986537, 0.14447 50.98656, 0.1445 50.986596, 0.144627 50.986643, 0.14473 50.986668, 0.145139 50.986737)))",  # noqa: E501
        "point": "POINT (-0.157398 51.546397)",
        "typology": "geography",
    }

    db_session.add(EntityOrm(**lp_entity))
    db_session.add(EntityOrm(**lpb_entity))

    params = {
        "reference": "1481207",
        "name": "Local-plan test",
        "dataset": "local-plan",
        "entity": 4220006,
        "local-plan-boundary": "E07000012",
    }

    linked_entities, boundary = fetch_linked_local_plans(db_session, params)
    assert hasattr(boundary, "geojson")
    assert "development-plan-timetable" in linked_entities
    assert linked_entities["development-plan-timetable"] == []
    assert linked_entities["development-plan-document"] == []
    assert "local-plan-housing" in linked_entities
    assert linked_entities["local-plan-housing"] == []


def test_fetch_linked_local_plans_housing(db_session):
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

    housing_entity = {
        "entity": 1100001,
        "name": "Local-plan-housing test",
        "entry_date": "2024-10-26",
        "start_date": "2024-10-26",
        "end_date": None,
        "dataset": "local-plan-housing",
        "json": {
            "local-plan": "1481207",
            "required-housing": 111,
            "allocated-housing": 222,
            "committed-housing": 333,
            "windfall-housing": 44,
            "broad-locations-housing": 555,
        },
        "organisation_entity": 123,
        "prefix": "local-plan-housing",
        "reference": "housing-ref-1",
        "typology": "legal-instrument",
    }

    db_session.add(EntityOrm(**lp_entity))
    db_session.add(EntityOrm(**housing_entity))

    params = {
        "reference": "1481207",
        "name": "Local-plan test",
        "dataset": "local-plan",
        "entity": 4220006,
        "local-plan-boundary": "E07000012",
    }

    linked_entities, boundary = fetch_linked_local_plans(db_session, params)

    assert boundary is None
    assert "local-plan-housing" in linked_entities
    housing_entities = linked_entities["local-plan-housing"]

    assert isinstance(housing_entities, list)
    assert len(housing_entities) == 1
    assert housing_entities[0].required_housing == 111
    assert housing_entities[0].allocated_housing == 222
    assert housing_entities[0].committed_housing == 333
    assert housing_entities[0].windfall_housing == 44
    assert housing_entities[0].broad_locations_housing == 555
