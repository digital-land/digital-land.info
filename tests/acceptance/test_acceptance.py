import pytest
import requests
import re

from playwright.sync_api import Page, expect


def test_acceptance(
    server_url,
    page,
    test_data,
):
    page.goto(server_url)

    page.click("text=Datasets")
    assert page.url == f"{server_url}/dataset/"
    assert page.text_content("h1") == "Datasets"
    page.goto(server_url)

    page.click("text=Map")
    assert page.url == f"{server_url}/map/"
    assert page.text_content("h1") == "Map of planning data for England"
    page.goto(server_url)

    page.click("text=Search")
    assert page.url == f"{server_url}/entity/"
    assert page.text_content("h1") == "Search for planning and housing data"
    page.goto(server_url)

    page.click("text=Datasets")
    assert page.url == f"{server_url}/dataset/"

    page.click("text=API")
    assert page.url == f"{server_url}/docs"
    assert page.text_content("h1") == "Documentation"
    page.goto(server_url)


# Anything which doesn't look at HTML can just be done with testClient which is more efficient
@pytest.mark.skip(reason="fixture to populate of data in test db not implemented yet")
def test_get_json(server_url):
    json_url = f"{server_url}/dataset/local-authority-eng.json"
    resp = requests.get(json_url)
    resp.raise_for_status()
    data = resp.json()

    assert data["collection"] == "organisation"
    assert data["dataset"] == "local-authority-eng"


# if json response use testClient to access it
def test_get_healthcheck(server_url):
    json_url = f"{server_url}/health"
    resp = requests.get(json_url)
    resp.raise_for_status()
    data = resp.json()

    assert data["status"] == "OK"


def test_documentation_page(server_url, page: Page):
    page.goto(server_url)
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


def test_documentation_page_error(server_url, page: Page):
    page.goto(server_url + "/docs")

    expect(page).not_to_have_title(
        re.compile("There is a problem with the service - Planning Data")
    )
