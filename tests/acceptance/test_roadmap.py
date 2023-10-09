def test_roadmap_loads_ok(server_process, BASE_URL, page):
    response = page.goto(BASE_URL + "/about/roadmap")
    assert response.ok
    heading = page.get_by_role(
        "heading",
        name="Roadmap",
    )
    assert heading.is_visible()
