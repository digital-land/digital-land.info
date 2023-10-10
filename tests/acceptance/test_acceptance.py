import pytest
import requests
import re

from playwright.sync_api import Page, expect


def test_acceptance(
    server_process,
    BASE_URL,
    page,
    test_data,
):
    page.goto(BASE_URL)

    page.click("text=Datasets")
    assert page.url == f"{BASE_URL}/dataset/"
    assert page.text_content("h1") == "Datasets"
    page.goto(BASE_URL)

    page.click("text=Map")
    assert page.url == f"{BASE_URL}/map/"
    assert page.text_content("h1") == "Map of planning data for England"
    page.goto(BASE_URL)

    page.click("text=Search")
    assert page.url == f"{BASE_URL}/entity/"
    assert page.text_content("h1") == "Search for planning and housing data"
    page.goto(BASE_URL)

    page.click("text=Datasets")
    assert page.url == f"{BASE_URL}/dataset/"

    page.click("text=Documentation")
    assert page.url == f"{BASE_URL}/docs"
    assert page.text_content("h1") == "Documentation"
    page.goto(BASE_URL)


@pytest.mark.skip(reason="fixture to populate of data in test db not implemented yet")
def test_get_json(server_process, BASE_URL):
    json_url = f"{BASE_URL}/dataset/local-authority-eng.json"
    resp = requests.get(json_url)
    resp.raise_for_status()
    data = resp.json()

    assert data["collection"] == "organisation"
    assert data["dataset"] == "local-authority-eng"


def test_get_healthcheck(server_process, BASE_URL):
    json_url = f"{BASE_URL}/health"
    resp = requests.get(json_url)
    resp.raise_for_status()
    data = resp.json()

    assert data["status"] == "OK"


def test_documentation_page(BASE_URL, page: Page):
    page.goto(BASE_URL)
    expect(page).to_have_title(re.compile("Planning Data"))
    documentation = page.get_by_role("link", name="Documentation", exact=True)
    expect(documentation).to_have_attribute("href", "/docs")
    documentation.click()

    documentation_url = page.url
    response = requests.get(documentation_url)

    assert response.status_code == 200, "Unexpected status code: {}".format(
        response.status_code
    )
    expect(page).to_have_url(re.compile(".*docs"))
    expect(page).to_have_title(re.compile("Documentation - Planning Data"))


def test_documentation_page_error(BASE_URL, page: Page):
    page.goto(BASE_URL + "/docs")

    expect(page).not_to_have_title(
        re.compile("There is a problem with the service - Planning Data")
    )
