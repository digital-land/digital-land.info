import re


def test_organisation_page_loads_ok(server_process, BASE_URL, page):
    response = page.goto(BASE_URL + "/organisation")
    assert response.ok
    heading = page.get_by_role(
        "heading",
        name="Organisations",
    )
    assert heading.is_visible()


def test_navigate_to_organisation_from_entity(server_process, BASE_URL, page):
    page.goto(BASE_URL)
    page.click("text=Search")

    page.locator("dd").filter(has_text=re.compile(r"^DAC$")).get_by_role("link").click()

    with page.expect_navigation() as navigation_info:
        page.get_by_role("link", name="organisation").click()

    assert navigation_info.value.ok
    assert BASE_URL + "/organisation" in navigation_info.value.url

    header = page.get_by_role("heading", name="Organisations")
    assert header.is_visible()
