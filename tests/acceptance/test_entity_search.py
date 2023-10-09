def test_blank_search(server_process, BASE_URL, page):
    page.goto(BASE_URL)
    page.click("text=Search")

    with page.expect_response("**/entity/**") as response:
        page.click("button:has-text(' Search ')")

    assert response.value.ok
