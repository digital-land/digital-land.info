def test_roadmap_loads_ok(server_url, page):
    response = page.goto(server_url + "/about/roadmap")
    assert response.ok
    heading = page.get_by_role(
        "heading",
        name="Roadmap",
    )
    assert heading.is_visible()
