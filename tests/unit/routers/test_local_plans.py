import pytest

from application.core.utils import to_snake
from application.routers.local_plans import list_local_plans
from application.routers.entity import fetch_linked_local_plans
from application.core.models import DatasetModel, EntityModel
from application.search.filters import DatasetQueryFilters


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
    mock_session = mocker.MagicMock()
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

    results, _boundary = fetch_linked_local_plans(mock_session, e_dict_sorted)

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


@pytest.mark.parametrize(
    "query_filters, expected_count",
    [
        (DatasetQueryFilters(), 2),
        (DatasetQueryFilters(dataset=["local-plan-boundary"]), 1),
        (
            DatasetQueryFilters(
                dataset=["local-plan-boundary"],
                field=["dataset,name,plural,collection"],
                exclude_field=["plural, collection"],
            ),
            1,
        ),
    ],
)
def test_list_local_plans(mocker, query_filters, expected_count):
    datasets = [
        DatasetModel(
            collection="local-plan",
            dataset="local-plan",
            name="Local plan",
            plural="Local plans",
            typology="legal-instrument",
        ),
        DatasetModel(
            collection="local-plan",
            dataset="local-plan-boundary",
            name="Local plan boundary",
            plural="Local plan boundaries",
            typology="geography",
        ),
    ]

    mocker.patch(
        "application.routers.local_plans.filter_datasets",
        return_value=datasets,
    )

    mocker.patch(
        "application.routers.local_plans.get_dataset_filter_fields",
        side_effect=lambda ds, include_fields: {
            key: value
            for key, value in ds.dict(by_alias=True).items()
            if key in include_fields
        },
    )

    result = list_local_plans(
        request=mocker.MagicMock(),
        extension=mocker.MagicMock(value="json"),
        query_filters=query_filters,
        session=mocker.MagicMock(),
    )

    assert result["feedback_form_footer"] is True
    assert len(result["datasets"]) == expected_count

    if query_filters and query_filters.field:
        assert "name" in result["datasets"][0]

    if query_filters and query_filters.exclude_field:
        excluded = {
            to_snake(part.strip())
            for item in query_filters.exclude_field
            for part in item.split(",")
            if part.strip()
        }
        for field in excluded:
            assert field not in result["datasets"][0]
