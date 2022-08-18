import time

import pytest
import requests
import uvicorn

from multiprocessing.context import Process
from application.settings import get_settings


settings = get_settings()

settings.READ_DATABASE_URL = (
    "postgresql://postgres:postgres@localhost/digital_land_test"
)
settings.WRITE_DATABASE_URL = (
    "postgresql://postgres:postgres@localhost/digital_land_test"
)

from application.app import create_app  # noqa: E402

app = create_app()

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


def test_acceptance(server_process, page, test_data):

    page.goto(BASE_URL)

    page.click("text=Datasets")
    assert page.url == f"{BASE_URL}/dataset/"
    assert page.text_content("h1") == "Datasets"
    page.goto(BASE_URL)

    page.click("text=Map")
    assert page.url == f"{BASE_URL}/map/"
    assert page.text_content("h1") == "National map of planning data"
    page.goto(BASE_URL)

    page.click("text=Search")
    assert page.url == f"{BASE_URL}/entity/"
    assert page.text_content("h1") == "Search for planning and housing data"
    page.goto(BASE_URL)

    page.click("text=Datasets")
    assert page.url == f"{BASE_URL}/dataset/"


@pytest.mark.skip(reason="fixture to populate of data in test db not implemented yet")
def test_get_json(server_process):
    json_url = f"{BASE_URL}/dataset/local-authority-eng.json"
    resp = requests.get(json_url)
    resp.raise_for_status()
    data = resp.json()

    assert data["collection"] == "organisation"
    assert data["dataset"] == "local-authority-eng"


def test_get_healthcheck(server_process):
    json_url = f"{BASE_URL}/health"
    resp = requests.get(json_url)
    resp.raise_for_status()
    data = resp.json()

    assert data["status"] == "OK"


def test_guidance_pages(server_process, page):

    page.goto(BASE_URL)

    page.click("text=Guidance")
    assert page.url == f"{BASE_URL}/guidance/"
    assert page.text_content("h1") == "Guidance for local planning authorities"

    page.click("text=Introduction")
    assert page.url == f"{BASE_URL}/guidance/introduction"
    page.click("text=Introduction for local planning authorities")

    page.click("text=How to provide data")
    assert page.url == f"{BASE_URL}/guidance/how-to-provide-data"

    page.click("text=How to provide data for local planning authorities")

    page.click("text=Data specifications guidance")
    assert page.url == f"{BASE_URL}/guidance/specifications/"

    page.click("text=Data specifications for local planning authorities")
