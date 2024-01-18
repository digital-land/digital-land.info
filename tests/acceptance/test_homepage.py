def test_homepage_loads_ok(server_url, page):
    response = page.goto(server_url)
    assert response.ok
    heading = page.get_by_role(
        "heading",
        name="Find planning and housing data that is easy to understand, use and trust",
    )
    assert heading.is_visible()
