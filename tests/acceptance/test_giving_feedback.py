import time

import pytest
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


def test_give_feedback_on_a_dataset(
    server_process, page, add_base_entities_to_database_yield_reset
):
    page.goto(BASE_URL)

    page.get_by_role("link", name="Datasets", exact=True).click()
    page.get_by_role("link", name="Geography").click()
    page.get_by_role("link", name="Brownfield site").click()
    page.get_by_role("link", name="Give feedback on this dataset").click()

    # ensure that the page has redirected to the google form
    assert "docs.google.com" in page.url
    assert page.get_by_role("heading", name="Give feedback on this dataset")

    # ensure the form has the correct dataset name
    assert (
        page.get_by_role(
            "textbox", name="Which dataset were you looking at?"
        ).input_value()
        == "Brownfield site"
    )
