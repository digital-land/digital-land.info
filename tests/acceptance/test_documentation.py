def test_docs_page_loads_ok(server_process, BASE_URL, page):
    response = page.goto(BASE_URL + "/docs/")
    assert response.ok
    heading = page.get_by_role(
        "heading",
        name="Documentation",
    )
    assert heading.is_visible()
