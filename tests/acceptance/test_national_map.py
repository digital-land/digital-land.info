import time

import pytest
import uvicorn

from multiprocessing.context import Process
from application.settings import get_settings

from playwright.sync_api import expect

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


def test_toggle_layers_on_the_national_map_correctly_shows_entity(
    server_process, page, add_base_entities_to_database_yield_reset
):

    page.goto(
        BASE_URL + "/map/#51.0560081663663,-2.260042873039197,10.722039104961226z"
    )
    page.get_by_label("Conservation area").check()
    page.wait_for_timeout(100)  # wait for map to load the conservation area layer
    page.get_by_role("region", name="Map").click(position={"x": 458, "y": 147})
    expect(page.get_by_text("Conservation areaStourton")).to_be_visible()
