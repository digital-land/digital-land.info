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
    page.get_by_role("link", name="Documentation", exact=True).click()

    with page.expect_navigation() as navigation_info:
        page.get_by_role(
            "link", name="https://www.planning.data.gov.uk/openapi.json"
        ).click()

    assert navigation_info.value.ok

    try:
        json.loads(navigation_info.value.body())
    except ValueError:
        assert False, "The openapi.json file is not valid JSON."

    page.go_back()

    linkHref = page.get_by_role("link", name="Swagger Editor").get_attribute("href")

    assert "swagger" in linkHref, "Link didn't contain 'swagger'"
    assert (
        "https://www.planning.data.gov.uk/openapi.json" in linkHref
    ), "Link didn't contain 'https://www.planning.data.gov.uk/openapi.json'"
