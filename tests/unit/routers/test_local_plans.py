import pytest

from unittest.mock import MagicMock
from application.routers.entity import fetch_linked_local_plans
from application.core.models import EntityModel


@pytest.fixture
def local_plan_model():
    model = EntityModel(
        entity=4220006,
        entry_date="2022-03-23",
        name="test-local-plan",
        reference="1481207",
        dataset="local-plan",
        prefix="local-plan",
        json={
            "adopted-date": "2018-09-27",
            "documentation-url": "https://www.scambs.gov.uk/planning/south-cambridgeshire-local-plan-2018",
            "local-plan-boundary": "E07000012",
        },
    )
    return model


@pytest.fixture
def local_plan_boundary_model():
    model = EntityModel(
        entity=4220006,
        entry_date="2022-03-23",
        name="test Local Plan boundary",
        reference="E1481201",
        dataset="local-plan-boundary",
        prefix="local-plan",
        json={
            "adopted-date": "2018-09-27",
            "documentation-url": "https://www.scambs.gov.uk/planning/south-cambridgeshire-local-plan-2018",
        },
        geojson={
            "type": "Feature",
            "geometry": {
                "type": "MultiPolygon",
                "coordinates": [
                    [
                        [
                            [0.145139, 50.986737],
                            [0.145088, 50.986778],
                            [0.14473, 50.986668],
                            [0.145139, 50.986737],
                        ]
                    ]
                ],
            },
        },
    )
    return model, None


@pytest.fixture
def local_plan_timetable_model():
    model1 = EntityModel(
        entity=4220005,
        entry_date="2022-03-23",
        name="test Local Plan timetable",
        reference="1481207",
        dataset="local-plan-timetable",
        prefix="local-plan-timetable",
        json={"event-date": "2018-11-20", "local-plan": "1481207"},
    )

    model2 = EntityModel(
        entity=4220006,
        entry_date="2022-03-23",
        name="test Local Plan timetable",
        reference="1481207",
        dataset="local-plan-timetable",
        prefix="local-plan-timetable",
        json={"event-date": "2020-11-20", "local-plan": "1481207"},
    )

    return [model1, model2]


@pytest.fixture
def local_plan_document_model():
    model1 = EntityModel(
        entity=4220007,
        entry_date="2022-03-23",
        name="test Local Plan Document",
        reference="1481207",
        dataset="local-plan-document",
        prefix="local-plan-document",
        json={
            "documentation-url": "https://www.arun.gov.uk/adopted-local-plan/",
            "local-plan": "1481207",
        },
    )

    return [model1]


def test_fetch_linked_local_plans_json_returned(
    mocker,
    local_plan_timetable_model,
    local_plan_document_model,
    local_plan_boundary_model,
):
    mock_session = MagicMock()
    mocker.patch(
        "application.routers.entity.linked_datasets",
        {
            "local-plan": ["local-plan-timetable", "local-plan-document"],
        },
    )

    mocker.patch(
        "application.routers.entity.get_linked_entities",
        side_effect=lambda session, dataset, reference, linked_dataset=None: {
            "local-plan-timetable": local_plan_timetable_model,
            "local-plan-document": local_plan_document_model,
            "local-plan-boundary": local_plan_boundary_model,
        }[
            dataset
        ],  # Return the appropriate model for the dataset
    )

    e_dict_sorted = {}
    e_dict_sorted["dataset"] = "local-plan"
    e_dict_sorted["reference"] = "1481207"

    results, boundary = fetch_linked_local_plans(mock_session, e_dict_sorted)

    # Assertions
    assert isinstance(results, dict), f"{type(results)} is expected to be a Dict"
    assert "local-plan-timetable" in results, "Expected local-plan-timetable in results"
    assert "local-plan-document" in results, "Expected local-plan-document in results"
    assert (
        len(results["local-plan-timetable"]) == 2
    ), "Expected 2 entities in 'local-plan-timetable'"
    assert (
        len(results["local-plan-document"]) == 1
    ), "Expected 1 entity in 'local-plan-document'"
