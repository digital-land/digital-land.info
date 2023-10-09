def test_about_loads_ok(server_process, BASE_URL, page):
    response = page.goto(BASE_URL + "/about")
    assert response.ok
    heading = page.get_by_role(
        "heading",
        name="About the Planning Data Platform",
    )
    assert heading.is_visible()
