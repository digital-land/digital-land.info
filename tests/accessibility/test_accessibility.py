import time

import pytest
import uvicorn

from multiprocessing.context import Process
from application.settings import get_settings
from axe_playwright_python.sync_playwright import Axe
from playwright.sync_api import sync_playwright

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

axe = Axe()


def run_server():
    uvicorn.run(app, host=HOST, port=PORT)


@pytest.fixture(scope="session")
def server_process():
    proc = Process(target=run_server, args=(), daemon=True)
    proc.start()
    time.sleep(10)
    yield proc
    proc.kill()


def accessibility_test(pageUrl):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.goto(pageUrl)
        results = axe.run(page)
        browser.close()

        print(f"Found {results.violations_count} violations for the page: {pageUrl}.")
        print(results.generate_report())

        assert results.violations_count == 0


def test_accessibility_of_homepage(server_process):
    accessibility_test(BASE_URL)


def test_accessibility_of_about_page(server_process):
    accessibility_test(BASE_URL + "/about")


def test_accessibility_of_dataset_index_page(server_process):
    accessibility_test(BASE_URL + "/dataset")


def test_accessibility_of_dataset_page(server_process):
    accessibility_test(BASE_URL + "/dataset/brownfield-site")


def test_accessibility_of_the_search_page(server_process):
    accessibility_test(BASE_URL + "/entity/?entries=current")


def test_accessibility_of_the_entity_page(server_process):
    accessibility_test(BASE_URL + "/entity/2")


def test_accessibility_of_the_map_page(server_process):
    accessibility_test(BASE_URL + "/map")


def test_accessibility_of_the_docs_page(server_process):
    accessibility_test(BASE_URL + "/docs")


def test_accessibility_of_the_guidance_index_page(server_process):
    accessibility_test(BASE_URL + "/guidance/")


def test_accessibility_of_the_guidance_intro_page(server_process):
    accessibility_test(BASE_URL + "/guidance/introduction")


def test_accessibility_of_the_guidance_how_to_provide_data_page(server_process):
    accessibility_test(BASE_URL + "/guidance/how-to-provide-data")


def test_accessibility_of_the_guidance_specifications_page(server_process):
    accessibility_test(BASE_URL + "/guidance/specifications")


def test_accessibility_of_the_service_status_page(server_process):
    accessibility_test(BASE_URL + "/service-status")


def test_accessibility_of_the_roadmap_page(server_process):
    accessibility_test(BASE_URL + "/about/roadmap")


def test_accessibility_of_the_accessibility_statement_page(server_process):
    accessibility_test(BASE_URL + "/accessibility-statement")
