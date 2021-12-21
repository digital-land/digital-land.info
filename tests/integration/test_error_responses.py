#!/usr/bin/env py.test
import pytest
from fastapi.testclient import TestClient
from dl_web.factory import create_app
from dl_web.settings import get_settings

"""
    We can't test any templated endpoint now we have middleware
    https://github.com/encode/starlette/issues/472
    until https://github.com/encode/starlette/pull/1071 is merged
    so we pick an arbitrary JSON endpoint
"""


@pytest.mark.skip(reason="await fix https://github.com/encode/starlette/issues/472")
def test_404_page():
    app = create_app()
    client = TestClient(app)
    response = client.get("/nopagehere")
    assert response.status_code == 404


@pytest.mark.skip(reason="await fix https://github.com/encode/starlette/issues/472")
def test_500_page():
    # break some settings so we can force an unhandled exception
    settings = get_settings()
    settings.DATASETTE_URL = "http://thiswontwork.com"
    app = create_app()
    client = TestClient(app)
    response = client.get("/entity")
    assert response.status_code == 500
