import json


def test_roadmap_loads_ok(server_process, BASE_URL, page):
    response = page.goto(BASE_URL + "/docs/")
    assert response.ok
    heading = page.get_by_role(
        "heading",
        name="Documentation",
    )
    assert heading.is_visible()


def test_accessing_the_openAPI_file_and_the_swagger_editor(
    server_process, BASE_URL, page
):
    page.goto(BASE_URL)
    page.get_by_role("link", name="Documentation", exact=True).click()

    with page.expect_navigation() as navigation_info:
        page.get_by_role(
            "link", name="https://www.planning.data.gov.uk/openapi.json"
        ).click()

    assert navigation_info.value.ok

    try:
        openapiJson = json.loads(navigation_info.value.body())
    except ValueError:
        assert False, "The openapi.json file is not valid JSON."

    page.go_back()

    with page.expect_navigation() as navigation_info:
        page.get_by_role("link", name="Swagger Editor").click()

    assert navigation_info.value.ok, "The Swagger Editor is not available."
    assert "swagger" in navigation_info.value.url, "Didn't navigate to Swagger Editor"

    heading = page.get_by_role(
        "heading",
        name=openapiJson["info"]["title"],
    )
    assert heading.is_visible()
