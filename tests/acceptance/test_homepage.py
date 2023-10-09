def test_homepage(server_process, BASE_URL, page):
    response = page.goto(BASE_URL)
    assert response.ok
    heading = page.get_by_role(
        "heading",
        name="Find planning and housing data that is easy to understand, use and trust",
    )
    assert heading.is_visible()
