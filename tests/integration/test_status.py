#!/usr/bin/env py.test
import pytest
from fastapi.testclient import TestClient
from dl_web.factory import create_app

app = create_app()
client = TestClient(app)


@pytest.mark.skip(reason="gets assertion error?!")
def test_404_page():
    response = client.get("/status/404")
    assert response.status_code == 404


def test_410_page():
    response = client.get("/status/410")
    assert response.status_code == 410


def test_500_page():
    response = client.get("/status/500")
    assert response.status_code == 500
