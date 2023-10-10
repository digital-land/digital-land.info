def test_organisation_page_loads_ok(server_process, BASE_URL, page):
    response = page.goto(BASE_URL + "/organisation")
    assert response.ok
    heading = page.get_by_role(
        "heading",
        name="Organisations",
    )
    assert heading.is_visible()
