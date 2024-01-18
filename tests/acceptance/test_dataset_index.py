def test_dataset_index_loads_ok(server_url, page):
    response = page.goto(server_url + "/dataset/")
    assert response.ok
    heading = page.get_by_role(
        "heading",
        name="Datasets",
    )
    assert heading.is_visible()
