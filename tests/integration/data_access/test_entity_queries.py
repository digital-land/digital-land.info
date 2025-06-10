import logging
import pytest

from application.db.models import EntityOrm
from application.data_access.entity_queries import get_entity_search

# set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.mark.parametrize(
    "entities, parameters, expected_count, expected_entities",
    [
        # a test case with a reference but onlly one
        (
            [
                {
                    "entity": 1,
                    "dataset": "conservation-area",
                    "reference": "CA1",
                    "geometry": "POLYGON((-0.39877874932762813 52.37557396590839,-0.49691286828496717 52.31309909388361,-0.3325311902998525 52.28924588007146,-0.280273249515528 52.35293530122911,-0.39877874932762813 52.37557396590839))",  # noqa E501
                },
                {
                    "entity": 2,
                    "reference": "CA2",
                    "dataset": "conservation-area",
                    "geometry": "POLYGON((-0.39877874932762813 52.37557396590839,-0.49691286828496717 52.31309909388361,-0.3325311902998525 52.28924588007146,-0.280273249515528 52.35293530122911,-0.39877874932762813 52.37557396590839))",  # noqa E501
                },
                {
                    "entity": 3,
                    "reference": "LPLAD1",
                    "dataset": "local-authority-district",
                    "geometry": "POLYGON((-0.7489300741242954 52.4863973669523,-0.9505678287521635 52.27316949066329,-0.3760369581498711 52.142463344337585,-0.21381926107403462 52.37856061047788,-0.7489300741242954 52.4863973669523))",  # noqa E501
                },
            ],
            {"dataset": ["conservation-area"], "geometry_reference": ["LPLAD1"]},
            2,
            [1, 2],
        ),
        # a test case with multiple entities uner the same reference
        (
            [
                {
                    "entity": 1,
                    "dataset": "conservation-area",
                    "reference": "CA1",
                    "geometry": "POLYGON((-0.39877874932762813 52.37557396590839,-0.49691286828496717 52.31309909388361,-0.3325311902998525 52.28924588007146,-0.280273249515528 52.35293530122911,-0.39877874932762813 52.37557396590839))",  # noqa E501
                },
                {
                    "entity": 2,
                    "reference": "CA2",
                    "dataset": "conservation-area",
                    "geometry": "POLYGON((-0.39877874932762813 52.37557396590839,-0.49691286828496717 52.31309909388361,-0.3325311902998525 52.28924588007146,-0.280273249515528 52.35293530122911,-0.39877874932762813 52.37557396590839))",  # noqa E501
                },
                {
                    "entity": 3,
                    "reference": "LPLAD1",
                    "dataset": "local-authority-district",
                    "geometry": "POLYGON((-0.7489300741242954 52.4863973669523,-0.9505678287521635 52.27316949066329,-0.3760369581498711 52.142463344337585,-0.21381926107403462 52.37856061047788,-0.7489300741242954 52.4863973669523))",  # noqa E501
                },
                {
                    "entity": 4,
                    "reference": "LPLAD1",
                    "dataset": "local-authority-district",
                    "geometry": "POLYGON((-0.07955040597019639 52.51338781409572,-0.5510502032408139 52.32210614595394,0.03009961574087244 52.18134255828252,-0.07955040597019639 52.51338781409572))",  # noqa E501
                },
            ],
            {"dataset": ["conservation-area"], "geometry_reference": ["LPLAD1"]},
            2,
            [1, 2],
        ),
    ],
)
def test_get_entity_search_geometry_reference_queries_returns_correct_results(
    entities, parameters, expected_count, expected_entities, db_session
):
    """
    A test to check if the correct results are returned when using the geometry_reference parameter
    """
    # load data points into entity table
    # add datasets
    for entity in entities:
        db_session.add(EntityOrm(**entity))

    # run query and get results
    results = get_entity_search(db_session, parameters)

    # assert count
    assert results["count"] == expected_count, results

    for entity in expected_entities:
        assert entity in [entity.entity for entity in results["entities"]], results


entities = [
    {
        "entity": 1,
        "dataset": "conservation-area",
        "reference": "CA1",
        "geometry": "POLYGON((-0.3 52.4, -0.4 52.3, -0.2 52.3, -0.3 52.4))",
    },
    {
        "entity": 2,
        "dataset": "flood-risk-zone",
        "reference": "FRZ1",
        "geometry": "POLYGON((-6.31 49.81, -6.29 49.81, -6.29 49.79, -6.31 49.79, -6.31 49.81))",
    },
]


@pytest.mark.parametrize(
    "entities, parameters, expected_count, expected_entities",
    [
        (
            [entities[0]],  # test case 1
            {"dataset": ["conservation-area"]},
            1,
            [entities[0]],
        ),
        (
            [entities[1]],  # test case 2
            {"dataset": ["flood-risk-zone"]},
            1,
            [entities[1]],
        ),
        (
            entities,  # test case 3: both
            {"dataset": ["flood-risk-zone", "conservation-area"]},
            2,
            entities,
        ),
    ],
)
def test_get_entity_search(
    db_session, entities, parameters, expected_count, expected_entities
):
    for entity in entities:
        db_session.add(EntityOrm(**entity))
    db_session.commit()

    result = get_entity_search(db_session, parameters)

    assert result["count"] > 0
    assert result["count"] == expected_count
    result_dataset = {e.dataset for e in result["entities"]}
    expected_dataset = {e["dataset"] for e in expected_entities}
    assert result_dataset == expected_dataset


def test_get_entity_search_apply_location_filters_geometry(db_session):
    entity = entities[0]
    db_session.add(EntityOrm(**entity))
    db_session.commit()

    # Query with a polygon that includes the above entity geometry
    result = get_entity_search(
        db_session,
        {
            "geometry": [
                "POLYGON((-0.07955040597019639 52.51338781409572, -0.5510502032408139 52.32210614595394,"
                " 0.03009961574087244 52.18134255828252, -0.07955040597019639 52.51338781409572))"
            ],
            "dataset": ["conservation-area"],
        },
    )

    assert result["count"] > 0
    for entity in result["entities"]:
        assert entity.dataset == "conservation-area"


def test_get_entity_search_with_point_filter(db_session):
    db_session.execute(
        """
        INSERT INTO entity (entity, dataset, reference, geometry)
        VALUES (
            2,
            'flood-risk-zone',
            'FRZ1',
            ST_GeomFromText('MULTIPOLYGON(((-6.352507 49.893859, -6.352647 49.893866,
            -6.352645 49.893844, -6.352611 49.893845, -6.35261 49.893834, -6.352507 49.893859)))', 4326)
        )
    """
    )
    db_session.execute(
        """
        INSERT INTO entity_subdivided (entity, dataset, geometry_subdivided)
        VALUES (
            2,
            'flood-risk-zone',
            ST_GeomFromText('MULTIPOLYGON(((-6.352507 49.893859, -6.352647 49.893866,
            -6.352645 49.893844, -6.352611 49.893845, -6.35261 49.893834, -6.352507 49.893859)))', 4326)
        )
    """
    )
    db_session.commit()
    params = {}
    params["longitude"] = -6.352593
    params["latitude"] = 49.893853
    params["dataset"] = ["flood-risk-zone"]

    result = get_entity_search(db_session, params)
    print(result)
    assert result["count"] == 1
    assert all(e.dataset == "flood-risk-zone" for e in result["entities"])


@pytest.mark.parametrize(
    "insert_subdivided, params, expected_count, expected_entities",
    [
        # Only entity table
        (
            False,
            {"geometry": ["POLYGON((-0.5 53, -0.1 53, -0.1 52, -0.5 52, -0.5 53))"]},
            1,
            [1],
        ),
        # Entity + subdivided
        (
            True,
            {
                "geometry": [
                    "POLYGON((-6.32 49.82, -6.28 49.82, -6.28 49.78, -6.32 49.78, -6.32 49.82))"
                ]
            },
            1,
            [2],
        ),
        # Both tables with geometry that matches only entity 1
        (
            True,
            {"geometry": ["POLYGON((-0.5 53, -0.1 53, -0.1 52, -0.5 52, -0.5 53))"]},
            1,
            [1],
        ),
    ],
)
def test_entity_search_with_entity_entity_subdivided_tables(
    db_session, insert_subdivided, params, expected_count, expected_entities
):
    for entity in entities:
        db_session.add(EntityOrm(**entity))
    db_session.commit()

    if insert_subdivided:
        db_session.execute(
            """
            INSERT INTO entity_subdivided (entity, dataset, geometry_subdivided)
            VALUES (
                2,
                'flood-risk-zone',
                ST_GeomFromText('POLYGON((-6.31 49.81, -6.29 49.81, -6.29 49.79, -6.31 49.79, -6.31 49.81))', 4326)
            )
            """
        )
        db_session.commit()

    result = get_entity_search(db_session, params)

    assert result["count"] == expected_count
    result_entities = [e.entity for e in result["entities"]]
    for e_id in expected_entities:
        assert e_id in result_entities
