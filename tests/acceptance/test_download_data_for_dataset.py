import time

import pytest
import uvicorn

from multiprocessing.context import Process
from application.settings import get_settings

import json

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


def test_download_data_for_dataset(
    server_process, page, add_base_entities_to_database_yield_reset
):
    page.goto(BASE_URL)

    page.get_by_role("link", name="Datasets", exact=True).click()
    page.get_by_role("link", name="Geography").click()
    page.get_by_role("link", name="Brownfield site").click()

    with page.expect_download() as download_info:
        page.get_by_role("link", name="CSV").click()

    # Check that the file name suggests that it is a CSV file
    assert "brownfield-site" in download_info.value.suggested_filename
    assert "csv" in download_info.value.suggested_filename

    # Check that the file content is valid JSON
    responseJson = page.text_content("body")
    json.loads(responseJson)

    # Go back to the Brownfield site dataset page
    page.go_back()

    # Check that the GeoJSON content is valid JSON
    page.get_by_role("link", name="GeoJSON").click()
    responseGeojson = page.text_content("body")
    json.loads(responseGeojson)
