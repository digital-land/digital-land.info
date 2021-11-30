import time

import pytest
import requests
import uvicorn
from multiprocessing.context import Process

from dl_web.app import app

HOST = "0.0.0.0"
PORT = 9000
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


def test_acceptance(server_process, page):

    assert server_process.is_alive()

    page.goto(f"{BASE_URL}")
    page.click("text=Datasets")
    assert page.url == f"{BASE_URL}/dataset/"
    page.click("text=Brownfield site")
    assert page.url == f"{BASE_URL}/dataset/brownfield-site"
    page.click('h1:has-text("Brownfield site")')
    page.click("text=Datasets")
    assert page.url == f"{BASE_URL}/dataset/"

    page.goto(f"{BASE_URL}/entity/")
    assert page.inner_text("h1") == "Search for planning and housing data"
    page.click("text=Ancient woodland")
    page.click('button:has-text("Search")')
    assert (
        page.url
        == f"{BASE_URL}/entity/?dataset=ancient-woodland&entries=all&entry_entry_date_day=&entry_entry_date_month=&entry_entry_date_year="
    )

    page.click("text=11345")
    assert page.url == f"{BASE_URL}/entity/11345"


def test_get_json(server_process):
    json_url = f"{BASE_URL}/entity/11345.json"
    resp = requests.get(json_url)
    resp.raise_for_status()
    data = resp.json()

    assert data["entity"] == "11345"
    assert data["entry-date"] == "2021-05-26"
    assert data["name"] == "WILK WOOD"
    assert data["dataset"] == "ancient-woodland"
    assert data["typology"] == "geography"
    assert data.get("geojson")
