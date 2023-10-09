def test_roadmap_loads_ok(server_process, BASE_URL, page):
    response = page.goto(BASE_URL + "/dataset/brownfield-site")
    assert response.ok
    heading = page.get_by_role(
        "heading",
        name="Brownfield site",
    )
    assert heading.is_visible()

    # make sure the total datasets is a number, and that the data providers is a number
