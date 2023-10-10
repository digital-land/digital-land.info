def test_dataset_index_loads_ok(server_process, BASE_URL, page):
    response = page.goto(BASE_URL + "/dataset/")
    assert response.ok
    heading = page.get_by_role(
        "heading",
        name="Datasets",
    )
    assert heading.is_visible()
