"""Check which entities spatial searches return, for cases the shared test data misses.

The shared test data has no entity whose point and geometry fall on different sides
of a search box, no entity with a geometry but no point, and no flood-risk-zone
entity with subdivided geometry. These tests add one of each, well away from the
shared data, and assert exactly which entities each search returns.
"""

import pytest
from sqlalchemy import text

from application.data_access.entity_queries import get_entity_search
from application.search.enum import GeometryRelation, PeriodOption

DATASET = "test-spatial"
OTHER_DATASET = "test-spatial-other"
FLOOD = "flood-risk-zone"


def square(west, south, east, north):
    return (
        f"POLYGON(({west} {south},{east} {south},{east} {north},"
        f"{west} {north},{west} {south}))"
    )


def multi(west, south, east, north):
    return (
        "MULTI" + square(west, south, east, north).replace("POLYGON", "POLYGON(") + ")"
    )


BOX = square(10, 10, 11, 11)

# Each entity: (id, name, dataset, geometry WKT or None, point WKT or None)
ENTITIES = [
    # Geometry and point both inside the box.
    (
        9_900_001,
        "both-inside",
        DATASET,
        multi(10.1, 10.1, 10.2, 10.2),
        "POINT(10.15 10.15)",
    ),
    # Geometry crosses the box edge, point outside it.
    (
        9_900_002,
        "geometry-crosses-point-outside",
        DATASET,
        multi(10.9, 10.9, 11.5, 11.5),
        "POINT(11.3 11.3)",
    ),
    # Point inside the box, geometry outside it.
    (
        9_900_003,
        "point-inside-geometry-outside",
        DATASET,
        multi(12, 12, 12.1, 12.1),
        "POINT(10.5 10.5)",
    ),
    # Geometry inside the box, no point, in a second dataset.
    (9_900_004, "geometry-only", OTHER_DATASET, multi(10.3, 10.3, 10.4, 10.4), None),
    # Point inside the box, no geometry.
    (9_900_005, "point-only", DATASET, None, "POINT(10.6 10.6)"),
    # Invalid (self-intersecting) geometry inside the box, valid point inside it.
    (
        9_900_006,
        "invalid-geometry-point-inside",
        DATASET,
        "MULTIPOLYGON(((10.7 10.7,10.8 10.8,10.8 10.7,10.7 10.8,10.7 10.7)))",
        "POINT(10.75 10.72)",
    ),
    # Invalid geometry inside the box, point outside it.
    (
        9_900_007,
        "invalid-geometry-point-outside",
        DATASET,
        "MULTIPOLYGON(((10.2 10.7,10.3 10.8,10.3 10.7,10.2 10.8,10.2 10.7)))",
        "POINT(13 13)",
    ),
    # Everything outside the box.
    (9_900_008, "outside", DATASET, multi(14, 14, 14.1, 14.1), "POINT(14.05 14.05)"),
]

# Flood risk zones are matched on their subdivided pieces.
FLOOD_INSIDE = 9_900_101
FLOOD_OUTSIDE = 9_900_102
SUBDIVIDED = [
    # Two pieces inside the box, so a naive join would return this entity twice.
    (FLOOD_INSIDE, multi(10.5, 10.1, 10.55, 10.2)),
    (FLOOD_INSIDE, multi(10.55, 10.1, 10.6, 10.2)),
    (FLOOD_OUTSIDE, multi(15, 15, 15.1, 15.1)),
]


@pytest.fixture
def spatial_entities(db_session):
    rows = [*ENTITIES]
    rows += [
        (FLOOD_INSIDE, "flood-inside", FLOOD, multi(10.5, 10.1, 10.6, 10.2), None),
        (FLOOD_OUTSIDE, "flood-outside", FLOOD, multi(15, 15, 15.1, 15.1), None),
    ]
    for entity, name, dataset, geometry, point in rows:
        db_session.execute(
            text(
                "INSERT INTO entity (entity, name, dataset, geometry, point) VALUES "
                "(:entity, :name, :dataset, ST_GeomFromText(:geometry, 4326), "
                "ST_GeomFromText(:point, 4326))"
            ),
            {
                "entity": entity,
                "name": name,
                "dataset": dataset,
                "geometry": geometry,
                "point": point,
            },
        )
    for entity, geometry in SUBDIVIDED:
        db_session.execute(
            text(
                "INSERT INTO entity_subdivided (entity, dataset, geometry_subdivided) "
                "VALUES (:entity, :dataset, ST_GeomFromText(:geometry, 4326))"
            ),
            {"entity": entity, "dataset": FLOOD, "geometry": geometry},
        )
    db_session.flush()


def ids(*names):
    lookup = {name: entity for entity, name, *_ in ENTITIES}
    lookup["flood-inside"] = FLOOD_INSIDE
    return sorted(lookup[name] for name in names)


INTERSECTS_ALL = ids(
    "both-inside",
    "geometry-crosses-point-outside",
    "point-inside-geometry-outside",
    "geometry-only",
    "point-only",
    "invalid-geometry-point-inside",
    "flood-inside",
)


@pytest.mark.parametrize(
    "dataset, relation, expected",
    [
        pytest.param(
            None, GeometryRelation.intersects, INTERSECTS_ALL, id="all-datasets"
        ),
        pytest.param(
            [DATASET],
            GeometryRelation.intersects,
            ids(
                "both-inside",
                "geometry-crosses-point-outside",
                "point-inside-geometry-outside",
                "point-only",
                "invalid-geometry-point-inside",
            ),
            id="one-dataset",
        ),
        pytest.param(
            [DATASET, OTHER_DATASET],
            GeometryRelation.intersects,
            ids(
                "both-inside",
                "geometry-crosses-point-outside",
                "point-inside-geometry-outside",
                "geometry-only",
                "point-only",
                "invalid-geometry-point-inside",
            ),
            id="two-datasets",
        ),
        pytest.param(
            [DATASET, FLOOD],
            GeometryRelation.intersects,
            ids(
                "both-inside",
                "geometry-crosses-point-outside",
                "point-inside-geometry-outside",
                "point-only",
                "invalid-geometry-point-inside",
                "flood-inside",
            ),
            id="dataset-and-flood-risk-zone",
        ),
        pytest.param(
            [FLOOD],
            GeometryRelation.intersects,
            ids("flood-inside"),
            id="flood-risk-zone-only",
        ),
        pytest.param(
            None,
            GeometryRelation.within,
            ids(
                "both-inside",
                "point-inside-geometry-outside",
                "geometry-only",
                "point-only",
                "invalid-geometry-point-inside",
                "flood-inside",
            ),
            id="all-datasets-within",
        ),
        pytest.param(
            [DATASET],
            GeometryRelation.within,
            ids(
                "both-inside",
                "point-inside-geometry-outside",
                "point-only",
                "invalid-geometry-point-inside",
            ),
            id="one-dataset-within",
        ),
    ],
)
def test_spatial_search_returns_expected_entities(
    db_session, spatial_entities, dataset, relation, expected
):
    result = get_entity_search(
        db_session,
        {
            "dataset": dataset,
            "geometry": [BOX],
            "geometry_relation": relation.name,
            "entries": PeriodOption.all,
            "limit": 100,
        },
    )
    returned = [entity.entity for entity in result["entities"]]
    assert sorted(returned) == expected
    # Each entity appears once, and the count agrees with the page.
    assert len(returned) == len(set(returned))
    assert result["count"] == len(expected)


@pytest.mark.parametrize(
    "dataset", [None, [DATASET]], ids=["all-datasets", "one-dataset"]
)
def test_spatial_search_with_several_geometries_returns_matches_for_any(
    db_session, spatial_entities, dataset
):
    around_both_inside = square(10.05, 10.05, 10.25, 10.25)
    around_point_only = square(10.55, 10.55, 10.65, 10.65)
    result = get_entity_search(
        db_session,
        {
            "dataset": dataset,
            "geometry": [around_both_inside, around_point_only],
            "geometry_relation": GeometryRelation.intersects.name,
            "entries": PeriodOption.all,
            "limit": 100,
        },
    )
    assert sorted(entity.entity for entity in result["entities"]) == ids(
        "both-inside", "point-only"
    )
    assert result["count"] == 2


def test_spatial_search_pages_cover_every_match_once(db_session, spatial_entities):
    seen = []
    for offset in range(0, len(INTERSECTS_ALL), 2):
        result = get_entity_search(
            db_session,
            {
                "geometry": [BOX],
                "geometry_relation": GeometryRelation.intersects.name,
                "entries": PeriodOption.all,
                "limit": 2,
                "offset": offset,
            },
        )
        assert result["count"] == len(INTERSECTS_ALL)
        seen += [entity.entity for entity in result["entities"]]
    assert seen == INTERSECTS_ALL
