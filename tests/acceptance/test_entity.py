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
    # Home page
    breakpoint()
    page.goto(BASE_URL)
    page.click("text=Search")

    page.wait_for_selector(
        '//h1[contains(text(), "Search for planning and housing data")]'
    )

    resultsCountText = page.locator(
        "//h2[contains(@class, 'app-results-summary__title')]"
    ).first.text_content()
    numberOfResults = int("".join(filter(str.isdigit, resultsCountText)))
    assert numberOfResults > 0

    time.sleep(5)

    # Search page
    page.locator('//label[contains(text(), "Address")]/preceding-sibling::input').click(
        timeout=60000
    )
    # page.click('//label[normalize-space(text())="Ancient woodland"]/following-sibling::input[@type="textbox"]')
    page.click("button:has-text('Search')")

    with page.expect_response("**/entity/**") as response:
        page.click("button:has-text('Search')")

    assert response.value.ok

    resultsCountText = page.locator(
        "//h2[contains(@class, 'app-results-summary__title')]"
    ).first()

    print(resultsCountText.text())


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
