from datetime import date

import pytest
from sqlalchemy import text
from application.data_access.entity_queries import get_entity_search
from application.search.enum import SuffixEntity
from application.db.models import EntityOrm


@pytest.fixture(params=["table", "view"])
def curie_entities(db_session, request):
    def polygon(size):
        return f"SRID=4326;MULTIPOLYGON(((0 0,{size} 0,{size} {size},0 {size},0 0)))"

    rows = [
        EntityOrm(entity=100, prefix="area", reference="A", geometry=polygon(10)),
        EntityOrm(entity=101, prefix="area", reference="A", geometry=polygon(12)),
        EntityOrm(entity=102, prefix="area", reference="B", geometry=polygon(8)),
        EntityOrm(entity=103, prefix="area", reference="null"),
        EntityOrm(
            entity=104,
            prefix="area",
            reference="invalid",
            geometry="SRID=4326;MULTIPOLYGON(((0 0,10 10,10 0,0 10,0 0)))",
        ),
        EntityOrm(
            entity=1,
            dataset="target",
            geometry=polygon(3),
            point="SRID=4326;POINT(2 2)",
        ),
        # The point must still match when the non-null geometry is outside.
        EntityOrm(
            entity=2,
            dataset="target",
            geometry="SRID=4326;MULTIPOLYGON(((20 20,21 20,21 21,20 21,20 20)))",
            point="SRID=4326;POINT(4 4)",
        ),
        EntityOrm(entity=3, dataset="target", point="SRID=4326;POINT(20 20)"),
        EntityOrm(
            entity=4,
            dataset="target",
            point="SRID=4326;POINT(5 5)",
            end_date=date(2000, 1, 1),
        ),
        EntityOrm(entity=5, dataset="target", geometry=polygon(2)),
    ]
    db_session.add_all(rows)
    db_session.flush()
    if request.param == "view":
        # Same data, but PostgreSQL cannot infer a primary key through a view.
        # The transaction rollback removes the view after each test.
        db_session.execute(
            text("CREATE TEMP VIEW entity AS SELECT * FROM public.entity")
        )


@pytest.mark.parametrize(
    "filters, expected",
    [
        ({"geometry_curie": ["area:A", "area:B"]}, [1, 2, 5]),
        # Preserve legacy multiplicity for one CURIE resolving to two boundaries.
        ({"geometry_curie": ["area:A"]}, [1, 1, 2, 2, 5, 5]),
        ({"geometry_curie": ["area:A", "area:A"]}, [1, 2, 5]),
        ({"geometry_curie": ["area:missing"]}, []),
        ({"geometry_curie": ["area:null", "area:invalid"]}, []),
        ({"geometry_curie": ["area:A", "area:B"], "period": ["historical"]}, [4]),
        ({"geometry_curie": ["area:A", "area:B"], "period": ["all"]}, [1, 2, 4, 5]),
        ({"geometry_curie": ["area:A"], "geometry_entity": [102]}, [1, 2, 5]),
        ({"geometry_curie": ["area:A"], "geometry_reference": ["B"]}, [1, 2, 5]),
        ({"geometry_curie": ["area:A"], "geometry_entity": [103]}, []),
        ({"geometry_curie": ["area:A"], "geometry_reference": ["missing"]}, []),
        ({"geometry_curie": ["area:A"], "longitude": 1, "latitude": 1}, [1, 1, 5, 5]),
        (
            {
                "geometry_curie": ["area:A"],
                "geometry": ["POLYGON((30 30,31 30,31 31,30 31,30 30))"],
            },
            [],
        ),
        ({}, [1, 2, 3, 5]),
        (
            {"geometry_curie": ["area:A", "area:B"], "geometry_relation": "intersects"},
            [1, 2, 5],
        ),
        ({"geometry_curie": ["area:A", "area:B"], "entity": [2]}, [2]),
        ({"geometry_curie": ["area:A", "area:B"], "dataset": ["other"]}, []),
    ],
)
@pytest.mark.parametrize("extension", [SuffixEntity.json, SuffixEntity.geojson, None])
def test_curie_split_results_and_count(
    db_session, curie_entities, filters, expected, extension
):
    params = {"dataset": ["target"], "period": ["current"], **filters}
    for pagination, expected_page in [
        ({}, expected),
        ({"offset": 1, "limit": 2}, expected[1:3]),
    ]:
        result = get_entity_search(db_session, {**params, **pagination}, extension)
        assert result["count"] == len(expected)
        # ORM results deduplicate entities; JSON column rows retain duplicates.
        if extension != SuffixEntity.json:
            expected_page = list(dict.fromkeys(expected_page))
        assert [entity.entity for entity in result["entities"]] == expected_page


@pytest.mark.parametrize("offset", [0, 100])
@pytest.mark.parametrize(
    "fields", [{"field": ["entity,name,json"]}, {"exclude_field": ["geometry,point"]}]
)
def test_shared_matches_fields_and_single_statement(
    db_session, curie_entities, offset, fields
):
    from sqlalchemy import event

    statements = []
    connection = db_session.connection()

    def record(conn, cursor, statement, parameters, context, executemany):
        statements.append(statement)

    event.listen(connection, "before_cursor_execute", record)
    try:
        result = get_entity_search(
            db_session,
            {
                "dataset": ["target"],
                "period": ["current"],
                "geometry_curie": ["area:A", "area:B"],
                "limit": 2,
                "offset": offset,
                **fields,
            },
            SuffixEntity.json,
        )
    finally:
        event.remove(connection, "before_cursor_execute", record)

    assert len(statements) == 1
    assert result["count"] == 3
    assert [e.entity for e in result["entities"]] == ([1, 2] if offset == 0 else [])
    assert all(e.geometry is None and e.point is None for e in result["entities"])
