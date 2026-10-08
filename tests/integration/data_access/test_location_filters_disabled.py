"""Regression coverage for the temporary dev diagnostic branch."""

from datetime import date

import pytest
from sqlalchemy import event

from application.data_access.entity_queries import get_entity_search
from application.db.models import EntityOrm
from application.search.enum import SuffixEntity


@pytest.mark.parametrize(
    "location_filters",
    [
        {"geometry_curie": ["area:missing"]},
        {"geometry_entity": [999]},
        {"geometry_reference": ["missing"]},
        {"geometry": ["POLYGON((30 30,31 30,31 31,30 31,30 30))"]},
        {"longitude": 30, "latitude": 30},
        {
            "geometry_curie": ["area:missing"],
            "geometry_entity": [999],
            "geometry_reference": ["missing"],
            "geometry": ["POLYGON((30 30,31 30,31 31,30 31,30 30))"],
            "longitude": 30,
            "latitude": 30,
        },
    ],
)
def test_search_ignores_location_filters(db_session, location_filters):
    db_session.add_all(
        [
            EntityOrm(entity=1, dataset="diagnostic", point="SRID=4326;POINT(1 1)"),
            EntityOrm(entity=2, dataset="diagnostic", point="SRID=4326;POINT(2 2)"),
            EntityOrm(entity=3, dataset="diagnostic", end_date=date(2000, 1, 1)),
            EntityOrm(entity=4, dataset="other"),
        ]
    )
    db_session.flush()
    statements = []
    connection = db_session.connection()

    def record(conn, cursor, statement, parameters, context, executemany):
        statements.append(statement)

    event.listen(connection, "before_cursor_execute", record)
    try:
        result = get_entity_search(
            db_session,
            {
                "dataset": ["diagnostic"],
                "period": ["current"],
                "limit": 1,
                "offset": 1,
                **location_filters,
            },
            SuffixEntity.json,
        )
    finally:
        event.remove(connection, "before_cursor_execute", record)

    assert result["count"] == 2
    assert [entity.entity for entity in result["entities"]] == [2]
    assert len(statements) == 2
    for statement in statements:
        assert "ST_Within" not in statement
        assert "ST_Contains" not in statement
        assert "ST_IsValid" not in statement
        assert "search_matches" not in statement
