def test_about_loads_ok(server_url, page):
    response = page.goto(server_url + "/about")
    assert response.ok
    heading = page.get_by_role(
        "heading",
        name="About the Planning Data Platform",
    )
    assert heading.is_visible()
