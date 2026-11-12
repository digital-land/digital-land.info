from contextlib import contextmanager
from unittest.mock import MagicMock, patch

import pytest
from bs4 import BeautifulSoup

from application.routers.entity import fetch_linked_local_plans, get_entity
from application.core.models import EntityModel
from application.db.models import EntityOrm
from application.search.enum import SuffixEntity


def test_entity_page_shows_organisation_name_not_none(
    client, db_session, test_data, exclude_middleware
):
    """
    Regression test: entity page must not render "None" for the Organisation field.

    Entity 101 (Dacorum Borough Council) in test data has organisation_entity=600001.
    When entity 600001 is in the DB, the router resolves it and the template renders
    its name via the get_entity_name filter. This test verifies the filter returns
    the actual name rather than Python None (which Jinja2 would render as the string "None").
    """
    # Use a distinct reference so the org-entity curie differs from entity 101's
    # own curie (local-authority:DAC), making the link href unambiguous on the page.
    org_entity = EntityOrm(
        entity=600001,
        name="Dacorum Borough Council",
        dataset="local-authority",
        typology="organisation",
        reference="E07000096",
        prefix="local-authority",
        entry_date="2022-01-01",
    )
    db_session.add(org_entity)
    db_session.flush()

    response = client.get("/entity/101", follow_redirects=True)

    assert response.status_code == 200

    soup = BeautifulSoup(response.text, "html.parser")
    org_link = soup.find("a", href="/curie/local-authority:E07000096")
    assert org_link is not None, "Organisation entity curie link not found in page"
    assert org_link.get_text(strip=True) == "Dacorum Borough Council"


def test_entity_page_side_nav_for_geography_entity(
    client, db_session, test_data, exclude_middleware
):
    """
    Assert that the side navigation renders all sections and links for a
    geography entity.

    Entity 1 (dataset "greenspace", typology "geography") has both geometry
    and a point in the test data, and the "greenspace" dataset has a
    "consideration" set - so all four side-nav sections should render.
    """
    response = client.get("/entity/1", follow_redirects=True)
    assert response.status_code == 200

    soup = BeautifulSoup(response.text, "html.parser")

    json_link = soup.find("a", href="/entity/1.json")
    assert json_link is not None, "JSON download link not found"
    assert json_link.get("download") == "1.json"

    geojson_link = soup.find("a", href="/entity/1.geojson")
    assert geojson_link is not None, "GeoJSON download link not found"
    assert geojson_link.get("download") == "1.geojson"

    map_link = soup.find(
        "a",
        href=lambda h: h
        and h.startswith("/map?dataset=greenspace#")
        and h.endswith(",15z"),
    )
    assert map_link is not None, "On a map link not found or malformed"

    definition_link = soup.find(
        "a", href="https://digital-land.github.io/specification/dataset/greenspace"
    )
    assert definition_link is not None, "Dataset definition link not found"

    design_link = soup.find(
        "a",
        href="https://design.planning.data.gov.uk/planning-consideration/greenspace",
    )
    assert design_link is not None, "Designing the data link not found"


def test_entity_page_side_nav_for_non_geography_entity(
    client, db_session, test_data, exclude_middleware
):
    """
    Assert that the side navigation omits the map and GeoJSON links for an
    entity with no geometry, and separately omits "Designing the data" for
    a dataset with no consideration set.

    Entity 101 (dataset "local-authority", typology "organisation") has no
    geometry/point, so the map link and GeoJSON download should be absent.
    Separately - and unrelated to geometry or typology - the
    "local-authority" dataset has no "consideration" set, so "Designing
    the data" should also be absent. JSON download and "Dataset
    definition" should still be present either way.
    """
    response = client.get("/entity/101", follow_redirects=True)
    assert response.status_code == 200

    soup = BeautifulSoup(response.text, "html.parser")

    json_link = soup.find("a", href="/entity/101.json")
    assert json_link is not None, "JSON download link not found"

    geojson_link = soup.find("a", href="/entity/101.geojson")
    assert geojson_link is None, "GeoJSON download link should not be shown"

    map_link = soup.find(
        "a", href=lambda h: h and h.startswith("/map?dataset=local-authority#")
    )
    assert map_link is None, "On a map link should not be shown"

    definition_link = soup.find(
        "a",
        href="https://digital-land.github.io/specification/dataset/local-authority",
    )
    assert definition_link is not None, "Dataset definition link not found"

    assert (
        soup.find(id="data-design") is None
    ), "Designing the data section should be absent"


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
        "local-plan-boundary": "E07000012",
    }

    linked_entities, boundary = fetch_linked_local_plans(db_session, params)

    assert boundary is None
    assert "local-plan-timetable" in linked_entities
    # Fetch the timetable entities
    timetable_entities = linked_entities["local-plan-timetable"]

    # Ensure timetable_entities is a list
    assert isinstance(
        timetable_entities, list
    ), "Expected timetable_entities to be a list"

    # Ensure at least one timetable entity exists
    assert len(timetable_entities) == 2, "Expected 2 timetable entity in 'local-plan'"
    # Both timetables share an event date, so their order is not defined.
    by_reference = {entity.reference: entity for entity in timetable_entities}
    published = by_reference["test-timetable"].local_plan_event
    assert isinstance(published, EntityModel)
    assert published.name == "Plan published"
    # Since it is estimated, it should not come in the list
    assert by_reference["test-timetable1"].local_plan_event is None


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
    assert "local-plan-timetable" in linked_entities
    assert linked_entities["local-plan-timetable"] == []
    assert linked_entities["local-plan-document"] == []


def test_entity_json_tab_escapes_html_in_field_values(
    client, db_session, test_data, exclude_middleware
):
    """Field values rendered in the entity JSON tab must be HTML-escaped so
    that attacker-controlled content cannot inject live markup.

    Entity field values are ingested from external data providers, so the JSON
    tab must escape them rather than mark them safe.
    """
    xss = '</code></pre><img src=x onerror="alert(1)">'
    script = "<script>alert(1)</script>"
    db_session.add(
        EntityOrm(
            entity=900900,
            name=xss,
            dataset="greenspace",
            typology="geography",
            reference="XSS-REF",
            prefix="greenspace",
            entry_date="2022-01-01",
            json={"attacker_field": script},
        )
    )
    db_session.flush()

    response = client.get("/entity/900900", follow_redirects=True)
    assert response.status_code == 200

    # The raw, executable payloads must not appear unescaped anywhere: not as a
    # live tag, and not as a raw <script> element.
    assert "<img src=x onerror=" not in response.text
    assert script not in response.text

    # No live element may have been injected into the DOM from our payload.
    soup = BeautifulSoup(response.text, "html.parser")
    assert soup.find("img", attrs={"onerror": True}) is None

    # The payload survives only as escaped text (in the "About this entity"
    # table, the heading/title, and the JSON tab).
    assert "&lt;img" in response.text
    assert "&lt;script&gt;" in response.text


GEOJSON_XSS_PAYLOAD = '<img src=x onerror="window.__xss=1">'


@pytest.fixture
def entity_with_html_in_json(db_session, test_data):
    """A geography entity whose publisher-supplied json holds an HTML payload.

    The payload ends up in the entity's GeoJSON properties, which the GeoJSON
    tab on the entity page fetches and displays.
    """
    db_session.add(
        EntityOrm(
            entity=900901,
            name="GeoJSON XSS entity",
            dataset="greenspace",
            typology="geography",
            reference="GEOJSON-XSS",
            prefix="greenspace",
            entry_date="2022-01-01",
            json={"notes": GEOJSON_XSS_PAYLOAD},
            geometry="MultiPolygon (((-0.33 53.74, -0.34 53.74, -0.34 53.75, -0.33 53.74)))",
            point="POINT (-0.335 53.745)",
        )
    )
    db_session.flush()

    @contextmanager
    def _context_session():
        yield db_session

    with patch(
        "application.data_access.entity_queries.get_context_session",
        _context_session,
    ):
        yield 900901


def test_get_entity_geojson_returns_publisher_html_unescaped(
    db_session, entity_with_html_in_json
):
    """The .geojson endpoint returns publisher values as raw data.

    This is correct for a data API, and it is why the page that displays this
    data must treat it as text rather than HTML.
    """
    geojson = get_entity(
        request=MagicMock(),
        entity=entity_with_html_in_json,
        extension=SuffixEntity.geojson,
        session=db_session,
    )

    assert geojson.properties["notes"] == GEOJSON_XSS_PAYLOAD


def test_get_entity_html_geojson_tab_writes_fetched_data_as_text(
    db_session, entity_with_html_in_json
):
    """The entity page must write fetched GeoJSON with textContent, not
    innerHTML, so HTML in publisher data is shown as text and never run."""
    response = get_entity(
        request=MagicMock(),
        entity=entity_with_html_in_json,
        extension=None,
        session=db_session,
    )
    assert response.status_code == 200

    soup = BeautifulSoup(response.body.decode(), "html.parser")
    geojson_script = next(
        (
            s.string
            for s in soup.find_all("script")
            if s.string and "loadGeoJSON" in s.string
        ),
        None,
    )
    assert geojson_script is not None, "GeoJSON tab script not found on page"

    assert "geojsonContentElement.innerHTML" not in geojson_script
    assert (
        "geojsonContentElement.textContent = JSON.stringify(JSON.parse(data)"
        in geojson_script
    )


UNSAFE_URL = "javascript:alert(1)"
SAFE_URL = "https://example.com/ok"


@pytest.fixture
def context_session(db_session):
    """Point get_entity_query at the test session so router functions can be
    called directly."""

    @contextmanager
    def _context_session():
        yield db_session

    with patch(
        "application.data_access.entity_queries.get_context_session",
        _context_session,
    ):
        yield


def _render_entity_page(db_session, entity_id):
    response = get_entity(
        request=MagicMock(), entity=entity_id, extension=None, session=db_session
    )
    assert response.status_code == 200
    return response.body.decode(), BeautifulSoup(response.body, "html.parser")


def _assert_no_javascript_links(soup):
    bad = [a["href"] for a in soup.find_all("a", href=True)]
    bad = [href for href in bad if href.strip().lower().startswith("javascript:")]
    assert bad == [], f"Unsafe links rendered: {bad}"


def test_get_entity_does_not_link_unsafe_urls_in_field_values(
    db_session, test_data, context_session
):
    db_session.add(
        EntityOrm(
            entity=4220100,
            name="Unsafe URL local plan",
            dataset="local-plan",
            typology="legal-instrument",
            prefix="local-plan",
            reference="UNSAFE-LP",
            entry_date="2022-01-01",
            json={
                "website": UNSAFE_URL,
                "documentation-url": UNSAFE_URL,
                "evidence-urls": f"{UNSAFE_URL}; {SAFE_URL}",
            },
        )
    )
    db_session.flush()

    html, soup = _render_entity_page(db_session, 4220100)

    _assert_no_javascript_links(soup)
    # The unsafe values are still shown, as text.
    assert UNSAFE_URL in soup.get_text()
    # Safe values in the same list are still links.
    assert soup.find("a", href=SAFE_URL) is not None


def test_get_entity_does_not_link_unsafe_local_plan_documentation_urls(
    db_session, test_data, context_session
):
    # A local plan page lists its documents (entity.html "Related Local Plan
    # Document" table).
    db_session.add(
        EntityOrm(
            entity=4220101,
            name="Local plan with documents",
            dataset="local-plan",
            typology="legal-instrument",
            prefix="local-plan",
            reference="LP-DOCS",
            entry_date="2022-01-01",
            json={},
        )
    )
    for entity_id, url in [(4220102, UNSAFE_URL), (4220103, SAFE_URL)]:
        db_session.add(
            EntityOrm(
                entity=entity_id,
                name=f"Document {entity_id}",
                dataset="local-plan-document",
                typology="document",
                prefix="local-plan-document",
                reference=f"LPD-{entity_id}",
                entry_date="2022-01-01",
                json={"local-plan": "LP-DOCS", "documentation-url": url},
            )
        )
    # A local plan boundary page lists its plans (entity.html "Related Local
    # Plans" table).
    db_session.add(
        EntityOrm(
            entity=4220104,
            name="Boundary",
            dataset="local-plan-boundary",
            typology="geography",
            prefix="local-plan-boundary",
            reference="LPB-UNSAFE",
            entry_date="2022-01-01",
            json={},
        )
    )
    db_session.add(
        EntityOrm(
            entity=4220105,
            name="Plan in boundary",
            dataset="local-plan",
            typology="legal-instrument",
            prefix="local-plan",
            reference="LP-IN-BOUNDARY",
            entry_date="2022-01-01",
            json={"local-plan-boundary": "LPB-UNSAFE", "documentation-url": UNSAFE_URL},
        )
    )
    db_session.flush()

    _, plan_soup = _render_entity_page(db_session, 4220101)
    assert "Related Local Plan Document" in plan_soup.get_text()
    _assert_no_javascript_links(plan_soup)
    assert UNSAFE_URL in plan_soup.get_text()
    assert plan_soup.find("a", href=SAFE_URL) is not None

    _, boundary_soup = _render_entity_page(db_session, 4220104)
    assert "Related Local Plans" in boundary_soup.get_text()
    _assert_no_javascript_links(boundary_soup)
    assert UNSAFE_URL in boundary_soup.get_text()
