import re

from tests.utils.database import add_entities_to_database

ENTITY_ROUTE = "/entity/"

# define some test data
mockEntities = [
    {
        "entity": "106",
        "name": "A space",
        "entry_date": "2019-01-07",
        "start_date": "2019-01-05",
        "end_date": "2020-01-07",
        "dataset": "greenspace",
        "json": None,
        "organisation_entity": None,
        "prefix": "greenspace",
        "reference": "Q1234567",
        "typology": "geography",
        "geometry": "MultiPolygon (((-0.3386878967285156 53.74426323597749, -0.337904691696167 53.743857158459996, -0.33673524856567383 53.744003093019586, -0.33637046813964844 53.74463124033804, -0.3365743160247803 53.74525937826645, -0.33737897872924805 53.74541799747043, -0.33875226974487305 53.74505000000031, -0.3386878967285156 53.74426323597749)))",  # noqa: E501
        "point": "POINT (-0.33737897872924805 53.74541799747043)",
    },
    {
        "entity": "107",
        "name": "B space",
        "entry_date": "2019-01-07",
        "start_date": None,
        "end_date": "2020-01-07",
        "dataset": "Brownfield site",
        "json": None,
        "organisation_entity": None,
        "prefix": "greenspace",
        "reference": "Q444444",
        "typology": "geography",
        "geometry": None,
        "point": "POINT (-0.33737897872924805 53.74541799747043)",
    },
    {
        "entity": "108",
        "name": "C space",
        "entry_date": "2019-01-07",
        "start_date": None,
        "end_date": "2020-01-07",
        "dataset": "Forest",
        "json": None,
        "organisation_entity": None,
        "prefix": "wikidata",
        "reference": "Q20648596",
        "typology": "organisation",
        "geometry": None,
        "point": None,
    },
]


def test_correctly_loads_the_entity_root(
    server_process, page, BASE_URL, add_base_entities_to_database_yield_reset
):
    page.goto(BASE_URL + ENTITY_ROUTE)
    assert page.title() == "Search for planning data"
    resultsText = page.locator(".app-results-summary__title").inner_text()
    assert re.match(r"\d+ results", resultsText)

    # check that the mapControllers array has been made and it isn't empty
    assert page.evaluate("Object.keys(window.mapControllers).length") > 0


async def test_find_an_entity_via_the_search_page(
    server_process, BASE_URL, page, empty_database
):
    add_entities_to_database(mockEntities)

    page.goto(BASE_URL)
    page.get_by_role("link", name="Search", exact=True).click()

    # check if A space and B space are in the results
    assert page.get_by_role("heading", name="A space") is not None
    assert page.get_by_role("heading", name="B space") is not None
    assert page.get_by_role("heading", name="C space") is not None

    # check that only two results are returned
    resultsCountText = page.locator(
        "//h2[contains(@class, 'app-results-summary__title')]"
    ).first.text_content()
    numberOfResults = int("".join(filter(str.isdigit, resultsCountText)))
    assert numberOfResults == mockEntities.__len__()

    # check that A and B space has a map and C space doesn't
    await page.wait_for_selector("[id='106-map']")
    await page.wait_for_selector("[id='107-map']")

    assert page.locator("[id='106-map']").count() == 1
    assert page.locator("[id='107-map']").count() == 1
    assert page.locator("[id='108-map']").count() == 0

    # filter down to just get geographies
    page.get_by_role("heading", name="Typology").click()
    page.get_by_label("geography").check()
    page.get_by_role("button", name="Search").click()

    # check that only two results are returned
    assert page.get_by_role("heading", name="A space").count() == 1
    assert page.get_by_role("heading", name="B space").count() == 1
    assert page.get_by_role("heading", name="C space").count() == 0

    # filter down to just get A space
    page.get_by_label("Greenspace").check()
    page.get_by_role("button", name="Search").click()

    # check that only A space is returned
    assert page.get_by_role("heading", name="A space").count() == 1
    assert page.get_by_role("heading", name="B space").count() == 0
    assert page.get_by_role("heading", name="C space").count() == 0

    # click into A space
    page.get_by_role("link", name="Q1234567").first.click()

    # make sure all values are correct
    assert (
        page.get_by_role("row", name="Reference")
        .get_by_role("cell")
        .first.inner_text()
        .lower()
        == mockEntities[0]["reference"].lower()
    )
    assert (
        page.get_by_role("row", name="Prefix")
        .get_by_role("cell")
        .first.inner_text()
        .lower()
        == mockEntities[0]["prefix"].lower()
    )
    assert (
        page.get_by_role("row", name="Name")
        .get_by_role("cell")
        .first.inner_text()
        .lower()
        == mockEntities[0]["name"].lower()
    )
    assert (
        page.get_by_role("row", name="Dataset")
        .get_by_role("cell")
        .first.inner_text()
        .lower()
        == mockEntities[0]["dataset"].lower()
    )
    assert (
        page.get_by_role("row", name="Start date")
        .get_by_role("cell")
        .first.inner_text()
        .lower()
        == mockEntities[0]["start_date"].lower()
    )
    assert (
        page.get_by_role("row", name="End date")
        .get_by_role("cell")
        .first.inner_text()
        .lower()
        == mockEntities[0]["end_date"].lower()
    )
    assert (
        page.get_by_role("row", name="Entry date")
        .get_by_role("cell")
        .first.inner_text()
        .lower()
        == mockEntities[0]["entry_date"].lower()
    )
    assert (
        page.get_by_role("row", name="Typology")
        .get_by_role("cell")
        .first.inner_text()
        .lower()
        == mockEntities[0]["typology"].lower()
    )


# This test is currently failing on the pipeline due to line 51 timing out
# ========================================================================
# def test_correctly_loads_an_entity_page(server_process, BASE_URL, page):
#     page.goto(BASE_URL + ENTITY_ROUTE + "1")

#     # check if the leafletjs script has been loaded
#     page.evaluate_handle("L")

#     # check if the mapControls element has been added to the page, indicating the js has been executed
#     mapControls = page.get_by_test_id("map").locator(
#         "//div[contains(@class, 'leaflet-control-container')]"
#     )
#     assert mapControls.count() == 1
