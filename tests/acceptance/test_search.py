def test_roadmap_loads_ok(server_process, BASE_URL, page):
    response = page.goto(BASE_URL + "/entity/")
    assert response.ok
    heading = page.get_by_role(
        "heading",
        name="Search for planning and housing data",
    )
    assert heading.is_visible()


def test_blank_search(server_process, BASE_URL, page):
    page.goto(BASE_URL)
    page.click("text=Search")

    with page.expect_response("**/entity/**") as response:
        page.click("button:has-text(' Search ')")

    assert response.value.ok
