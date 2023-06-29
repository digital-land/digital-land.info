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

    mapControls = page.get_by_test_id("map").locator(
        "//div[contains(@class, 'leaflet-control-container')]"
    )
    assert mapControls.count() > 1


def test_correctly_loads_an_entity_page(server_process, page):
    page.goto(BASE_URL + ENTITY_ROUTE + "1")

    # check if the leafletjs script has been loaded
    page.evaluate_handle("L")

    # check if the map js object has been made
    page.evaluate_handle("mapComponent")

    # check if the map control element have been made (indicating the leaflet js has been loaded)
    mapControls = page.locator(
        "//div[@id='dlMap']//div[contains(@class, 'leaflet-control-container')]"
    )
    mapControls = page.get_by_test_id("map").locator(
        "//div[contains(@class, 'leaflet-control-container')]"
    )
    assert mapControls.count() == 1
