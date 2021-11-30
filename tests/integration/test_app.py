from fastapi.testclient import TestClient

from dl_web.factory import create_app

app = create_app()
client = TestClient(app)


def test_response_cors_headers():
    """
    Test that the appropriate CORS headers are included in a simple GET request to server root
    """
    response = client.get("/", headers={"Origin": "localhost"})
    assert "Access-Control-Allow-Origin" in response.headers.keys()
    assert response.headers["Access-Control-Allow-Origin"] == "*"
