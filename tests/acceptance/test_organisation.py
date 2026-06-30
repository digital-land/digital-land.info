def test_organisation_page_loads_ok(server_url, page):
    response = page.goto(server_url + "/organisation")
    assert response.ok
    heading = page.get_by_role(
        "heading",
        name="Organisations",
    )
    assert heading.is_visible()


def test_navigate_to_organisation_from_entity(server_url, page, app_test_data):
    response = page.goto(server_url)
    assert response is not None and response.ok

    entity_link = page.locator("a[href='/entity']:visible").first
    assert entity_link.is_visible()
    entity_link.click()
    page.wait_for_load_state("networkidle")

    dac_link = page.get_by_role("link", name="DAC").first
    assert dac_link.is_visible()
    dac_link.click()
    page.wait_for_load_state("networkidle")

    org_link = page.get_by_role("link", name="organisation", exact=True)
    assert org_link.is_visible()
    with page.expect_navigation() as navigation_info:
        org_link.click()

    assert navigation_info.value.ok
    assert server_url + "/organisation" in navigation_info.value.url

    header = page.get_by_role("heading", name="Organisations")
    assert header.is_visible()
