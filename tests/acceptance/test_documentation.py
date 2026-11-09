import json


def test_docs_page_loads_ok(server_url, page):
    response = page.goto(server_url + "/docs/")
    assert response.ok
    heading = page.get_by_role(
        "heading",
        name="Documentation",
    )
    assert heading.is_visible()


def test_accessing_the_openAPI_file_and_the_swagger_editor(server_url, page):
    page.goto(server_url)
    page.get_by_role("link", name="API", exact=True).click()

    # The docs page links to the canonical production OpenAPI URL as product
    # content. Assert the link is present without navigating to the live
    # service, then validate the OpenAPI document served by this instance.
    openapi_link = page.get_by_role(
        "link", name="https://www.planning.data.gov.uk/openapi.json"
    )
    assert openapi_link.is_visible()

    response = page.request.get(server_url + "/openapi.json")
    assert response.ok

    try:
        json.loads(response.body())
    except ValueError:
        assert False, "The openapi.json file is not valid JSON."

    linkHref = page.get_by_role("link", name="Swagger Editor").get_attribute("href")

    assert "swagger" in linkHref, "Link didn't contain 'swagger'"
    assert (
        "https://www.planning.data.gov.uk/openapi.json" in linkHref
    ), "Link didn't contain 'https://www.planning.data.gov.uk/openapi.json'"
