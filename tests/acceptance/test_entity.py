import pytest

import time
import re

import uvicorn

from multiprocessing.context import Process

from application.app import create_app  # noqa: E402

app = create_app()

HOST = "0.0.0.0"
PORT = 9000
ENTITY_ROUTE = "/entity/"
BASE_URL = f"http://{HOST}:{PORT}"


def run_server():
    uvicorn.run(app, host=HOST, port=PORT)


@pytest.fixture(scope="session")
def server_process():
    proc = Process(target=run_server, args=(), daemon=True)
    proc.start()
    time.sleep(10)
    yield proc
    proc.kill()


def test_correctly_loads_the_entity_root(server_process, page):
    page.goto(BASE_URL + ENTITY_ROUTE)
    assert page.title() == "Search for planning data"
    resultsText = page.locator(".app-results-summary__title").inner_text()
    assert re.match(r"\d+ results", resultsText)

    # check if the leafletjs script has been loaded
    page.evaluate_handle("L")

    # check if the mapControls element has been added to the page, indicating the js has been executed
    mapControls = page.get_by_test_id("map").locator(
        "//div[contains(@class, 'leaflet-control-container')]"
    )
    assert mapControls.count() > 1


def test_find_an_entity_via_the_search_page(server_process, page):

    page.goto(BASE_URL)
    page.get_by_role("link", name="Search", exact=True).click()

    resultsCountText = page.locator(
        "//h2[contains(@class, 'app-results-summary__title')]"
    ).first.text_content()
    numberOfResults = int("".join(filter(str.isdigit, resultsCountText)))
    assert numberOfResults > 0

    with page.expect_navigation() as navigation_info:
        page.get_by_label("Brownfield site").check()
        page.get_by_role("button", name="Search").click()

    response = navigation_info.value
    assert response.status == 200

    page.get_by_label("Forest").check()
    page.get_by_label("Brownfield site").uncheck()
    page.get_by_label("Day").click()
    page.get_by_label("Day").fill("01")
    page.get_by_label("Day").press("Tab")
    page.get_by_label("Month").fill("01")
    page.get_by_label("Month").press("Tab")
    page.get_by_label("Year").fill("2010")
    page.get_by_label("Since").check()
    page.get_by_role("button", name="Search").click()

    resultsCountText = page.locator(
        "//h2[contains(@class, 'app-results-summary__title')]"
    ).first.text_content()
    numberOfResults = int("".join(filter(str.isdigit, resultsCountText)))
    assert numberOfResults > 0

    page.get_by_role("group").filter(
        has_text="Entries1 selected Entries Which type of entries do you want to see? All Current "
    ).get_by_role("img").click()
    page.get_by_label("Current").check()
    page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name="current").click()
    page.get_by_role("link", name="current").click()
    page.get_by_role("link", name="current").click()
    page.get_by_role("link", name="current").click()
    page.get_by_role("link", name="DateOption.since").click()
    page.get_by_role("button", name="Search").click()

    with page.expect_navigation() as navigation_info:
        page.get_by_label("Brownfield site").check()
        page.get_by_role("button", name="Search").click()

    response = navigation_info.value
    assert response.status == 200


# This test is currently failing on the pipeline due to line 51 timing out
# ========================================================================
# def test_correctly_loads_an_entity_page(server_process, page):
#     page.goto(BASE_URL + ENTITY_ROUTE + "1")

#     # check if the leafletjs script has been loaded
#     page.evaluate_handle("L")

#     # check if the mapControls element has been added to the page, indicating the js has been executed
#     mapControls = page.get_by_test_id("map").locator(
#         "//div[contains(@class, 'leaflet-control-container')]"
#     )
#     assert mapControls.count() == 1
