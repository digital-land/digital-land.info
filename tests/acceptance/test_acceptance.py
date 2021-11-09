import time

import pytest
import uvicorn
from multiprocessing.context import Process

from dl_web.app import app

HOST = "0.0.0.0"
PORT = 9000
BASE_URL = f"http://{HOST}:{PORT}"


def run_server():
    uvicorn.run(app, host=HOST, port=PORT)


@pytest.fixture
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
