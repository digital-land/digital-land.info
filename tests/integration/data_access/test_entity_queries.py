import logging
import pytest

from application.db.models import EntityOrm
from application.data_access.entity_queries import get_entity_search
from sqlalchemy.orm import Query
from application.data_access.entity_queries import (
    _apply_location_filters,
)

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


def test__apply_location_filters_with_only_frz(db_session):
    query = Query(EntityOrm)
    result = _apply_location_filters(
        db_session,
        query,
        params={
            "longitude": "-0.2",
            "latitude": "53.38",
            "dataset": ["flood-risk-zone"],
        },
    )
    sql_str = str(result.statement.compile(compile_kwargs={"literal_binds": True}))
    assert "entity_subdivided" in sql_str


def test__apply_location_filters_with_frz_and_others(db_session):
    query = Query(EntityOrm)
    result = _apply_location_filters(
        db_session,
        query,
        params={
            "longitude": "-0.2",
            "latitude": "53.38",
            "dataset": ["flood-risk-zone", "conservation-area"],
        },
    )
    sql_str = str(result.statement.compile(compile_kwargs={"literal_binds": True}))
    assert "entity_subdivided" not in sql_str


def test__apply_location_filters_without_frz(db_session):
    query = Query(EntityOrm)
    result = _apply_location_filters(
        db_session,
        query,
        params={
            "longitude": "-0.2",
            "latitude": "53.38",
            "dataset": ["conservation-area"],
        },
    )
    sql_str = str(result.statement.compile(compile_kwargs={"literal_binds": True}))
    assert "entity_subdivided" not in sql_str


def test__apply_location_filters_with_only_frz_geom(db_session):
    query = Query(EntityOrm)
    result = _apply_location_filters(
        db_session,
        query,
        params={"geometry": "MULTIPOLYGON(-2.1 51.3)", "dataset": ["flood-risk-zone"]},
    )
    sql_str = str(result.statement.compile(compile_kwargs={"literal_binds": True}))
    assert "entity_subdivided" in sql_str


def test__apply_location_filters_with_frz_and_others_geom(db_session):
    query = Query(EntityOrm)
    result = _apply_location_filters(
        db_session,
        query,
        params={
            "geometry": "MULTIPOLYGON(-2.1 51.3)",
            "dataset": ["flood-risk-zone", "conservation-area"],
        },
    )
    sql_str = str(result.statement.compile(compile_kwargs={"literal_binds": True}))
    assert "entity_subdivided" not in sql_str


def test__apply_location_filters_without_frz_geom(db_session):
    query = Query(EntityOrm)
    result = _apply_location_filters(
        db_session,
        query,
        params={
            "geometry": "MULTIPOLYGON(-2.1 51.3)",
            "dataset": ["conservation-area"],
        },
    )
    sql_str = str(result.statement.compile(compile_kwargs={"literal_binds": True}))
    assert "entity_subdivided" not in sql_str
