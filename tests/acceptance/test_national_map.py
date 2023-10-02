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


def wait_for_map_layer(page, layer, attempts=10, check_interval=10):
    for i in range(attempts):
        isHidden = page.evaluate(
            f'() => mapControllers.map.map.getLayer("{layer}").isHidden()'
        )
        if isHidden is False:
            return True
        page.wait_for_timeout(check_interval)
    assert False, f"Layer {layer} did not appear on the map"


def test_toggle_layers_on_the_national_map_correctly_shows_entity(
    server_process, page, add_base_entities_to_database_yield_reset
):
    # as the map xy coords are dependent on the viewport size, we need to set it to make sure the tests are consistent
    page.set_viewport_size({"width": 800, "height": 600})
    page.goto(
        BASE_URL + "/map/#50.88865897214836,-2.260771340418273,11.711391365982688z"
    )
    page.get_by_label("Conservation area").check()
    wait_for_map_layer(page, "conservation-area-source-fill-extrusion")
    # note:
    # even with the viewport set to a fixed size this click doesn't always happen in the same place between browsers
    page.get_by_label("Map").click(position={"x": 329, "y": 300})
    expect(page.get_by_text("Conservation area")).to_be_visible()
