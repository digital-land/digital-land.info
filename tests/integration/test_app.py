from fastapi.testclient import TestClient

from dl_web.settings import get_settings
from dl_web.factory import create_app

settings = get_settings()
settings.DATASETTE_URL = "https://datasette.digital-land.info"
settings.S3_COLLECTION_BUCKET = "https://collection-dataset.s3.eu-west-2.amazonaws.com"
settings.READ_DATABASE_URL = "postgresql://postgres:postgres@localhost/digitalland"
settings.WRITE_DATABASE_URL = "postgresql://postgres:postgres@localhost/digitalland"

app = create_app()

client = TestClient(app)

SECONDS_IN_TWO_YEARS = 63072000.0


def test_response_cors_headers():
    """
    Test that the appropriate CORS headers are included in a simple GET request to server root

    We can't test any templated endpoint now we have middleware
    https://github.com/encode/starlette/issues/472
    until https://github.com/encode/starlette/pull/1071 is merged
    so we pick an arbitrary JSON endpoint
    """
    response = client.get("/entity.json", headers={"Origin": "localhost"})
    assert "Access-Control-Allow-Origin" in response.headers.keys()
    assert response.headers["Access-Control-Allow-Origin"] == "*"


def test_response_strict_transport_security_header():
    """
    Test that the correct HSTS header is included in a simple GET request to server root

    We can't test any templated endpoint here due to:
    https://github.com/encode/starlette/issues/472
    until https://github.com/encode/starlette/pull/1071 is merged
    so we pick an arbitrary JSON endpoint
    """
    expected_header = f"max-age={SECONDS_IN_TWO_YEARS}; includeSubDomains; preload"
    response = client.get("/entity.json", headers={"Origin": "localhost"})
    assert "Strict-Transport-Security" in response.headers.keys()
    assert response.headers["Strict-Transport-Security"] == expected_header


def test_x_frame_options_header():
    """
    Test that the correct X-Frame-Options header is included in a simple GET request to server root

    We can't test any templated endpoint here due to:
    https://github.com/encode/starlette/issues/472
    until https://github.com/encode/starlette/pull/1071 is merged
    so we pick an arbitrary JSON endpoint
    """
    response = client.get("/entity.json", headers={"Origin": "localhost"})
    assert "X-Frame-Options" in response.headers.keys()
    assert response.headers["X-Frame-Options"] == "sameorigin"


def test_x_content_type_options_header():
    """
    Test that the correct X-Content-Type-Options header is included in a simple GET request to server root

    We can't test any templated endpoint here due to:
    https://github.com/encode/starlette/issues/472
    until https://github.com/encode/starlette/pull/1071 is merged
    so we pick an arbitrary JSON endpoint
    """
    response = client.get("/entity.json", headers={"Origin": "localhost"})
    assert "X-Content-Type-Options" in response.headers.keys()
    assert response.headers["X-Content-Type-Options"] == "nosniff"
