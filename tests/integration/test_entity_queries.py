from application.data_access.entity_queries import lookup_entity_link
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
