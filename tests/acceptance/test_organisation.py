def test_organisation_page_loads_ok(server_url, page):
    response = page.goto(server_url + "/organisation")
    assert response.ok
    heading = page.get_by_role(
        "heading",
        name="Organisations",
    )
    assert heading.is_visible()


def test_navigate_to_organisation_from_entity(server_url, page, app_test_data):
    page.goto(server_url)
    page.click("text=Search")

    page.get_by_role("link", name="DAC").first.click()

    with page.expect_navigation() as navigation_info:
        page.get_by_role("link", name="organisation", exact=True).click()

    assert navigation_info.value.ok
    assert server_url + "/organisation" in navigation_info.value.url

    header = page.get_by_role("heading", name="Organisations")
    assert header.is_visible()
