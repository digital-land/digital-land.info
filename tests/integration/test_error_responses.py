#!/usr/bin/env py.test
import pytest

"""
    We can't test any templated endpoint now we have middleware
    https://github.com/encode/starlette/issues/472
    until https://github.com/encode/starlette/pull/1071 is merged
    so we pick an arbitrary JSON endpoint
"""


@pytest.mark.skip(reason="await fix https://github.com/encode/starlette/issues/472")
def test_404_page(client):
    response = client.get("/nopagehere")
    assert response.status_code == 404


@pytest.mark.skip(reason="await fix https://github.com/encode/starlette/issues/472")
def test_500_page(client, test_settings):
    # break some settings so we can force an unhandled exception
    test_settings.DATASETTE_URL = "http://thiswontwork.com"
    response = client.get("/entity")
    assert response.status_code == 500
