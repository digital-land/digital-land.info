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


def test_blank_search(server_process, page):
    page.goto(BASE_URL)
    page.click("text=Search")

    with page.expect_response("**/entity/**") as response:
        page.click("button:has-text(' Search ')")

    assert response.value.ok
