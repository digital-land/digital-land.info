from bs4 import BeautifulSoup

from application.core.templates import templates


def test_status_banner_shown_when_service_status_toggled_on(
    client, exclude_middleware, monkeypatch
):
    monkeypatch.setitem(templates.env.globals, "serviceStatus", True)

    response = client.get("/")

    assert response.status_code == 200
    soup = BeautifulSoup(response.text, "html.parser")
    assert soup.find(class_="govuk-notification-banner") is not None


def test_status_banner_hidden_when_service_status_toggled_off(
    client, exclude_middleware, monkeypatch
):
    monkeypatch.setitem(templates.env.globals, "serviceStatus", False)

    response = client.get("/")

    assert response.status_code == 200
    soup = BeautifulSoup(response.text, "html.parser")
    assert soup.find(class_="govuk-notification-banner") is None
