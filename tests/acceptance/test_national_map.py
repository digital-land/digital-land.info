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


def test_toggle_layers_on_the_national_map_correctly_shows_entity(
    server_process, page, add_base_entities_to_database_yield_reset
):
    # as the map xy coords are dependent on the viewport size, we need to set it to make sure the tests are consistent
    page.set_viewport_size({"width": 800, "height": 600})
    page.goto(
        BASE_URL + "/map/#50.88865897214836,-2.260771340418273,11.711391365982688z"
    )
    page.wait_for_selector("label.govuk-checkboxes__label", timeout=120000)
    isHiddenBeforeClicking = page.evaluate(
        'mapControllers.map.map.getLayer("conservation-area-source-fill-extrusion").isHidden()'
    )
    if not isHiddenBeforeClicking:
        raise Exception(
            "conservation-area-source-fill-extrusion should be hidden on page load"
        )
    page.get_by_label("Conservation area").check()
    isHiddenAfterClicking = page.evaluate(
        'mapControllers.map.map.getLayer("conservation-area-source-fill-extrusion").isHidden()'
    )
    if isHiddenAfterClicking:
        raise Exception(
            "conservation-area-source-fill-extrusion should not be hidden after clicking the layer"
        )
