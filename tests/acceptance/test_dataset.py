def test_dataset_page_loads_ok(
    server_process, BASE_URL, page, add_base_entities_to_database_yield_reset
):
    response = page.goto(BASE_URL + "/dataset/brownfield-site")
    assert response.ok
    heading = page.get_by_role(
        "heading",
        name="Brownfield site",
    )
    assert heading.is_visible()


def test_download_data_for_dataset(
    server_process, BASE_URL, page, add_base_entities_to_database_yield_reset
):
    page.goto(BASE_URL)

    # Navigate to the Brownfield site dataset page.
    page.get_by_role("link", name="Datasets", exact=True).click()
    page.get_by_role("link", name="Geography").click()
    page.get_by_role("link", name="Brownfield site").click()

    # Check that the "CSV" download link is correct.
    csv_href = page.get_by_role("link", name="CSV", exact=True).first.get_attribute(
        "href"
    )

    assert "brownfield-site" in csv_href
    assert ".csv" in csv_href

    # Check that the "JSON" download link is correct.
    json_href = page.get_by_role("link", name="JSON", exact=True).first.get_attribute(
        "href"
    )

    assert "brownfield-site" in json_href
    assert ".json" in json_href

    # Check that the "GeoJSON" download link is correct.
    geojson_href = page.get_by_role(
        "link", name="GeoJSON", exact=True
    ).first.get_attribute("href")

    assert "brownfield-site" in geojson_href
    assert ".geojson" in geojson_href


def test_navigate_to_a_dataset_specification(
    server_process, BASE_URL, page, add_base_entities_to_database_yield_reset
):
    page.goto(BASE_URL)
    page.get_by_role("link", name="Datasets", exact=True).click()
    page.get_by_role("link", name="Geography").click()
    with page.expect_navigation() as response:
        page.get_by_role("link", name="Brownfield site").click()
    assert response.value.ok
    heading = page.get_by_role(
        "heading",
        name="Brownfield site",
    )
    assert heading.is_visible()


def test_give_feedback_on_a_dataset(
    server_process, BASE_URL, page, add_base_entities_to_database_yield_reset
):
    page.goto(BASE_URL)

    page.get_by_role("link", name="Datasets", exact=True).click()
    page.get_by_role("link", name="Geography").click()
    page.get_by_role("link", name="Brownfield site").click()
    page.get_by_role("link", name="Give feedback on this dataset").click()

    # ensure that the page has redirected to the google form
    assert "docs.google.com" in page.url
    assert page.get_by_role("heading", name="Give feedback on this dataset")

    # had to add this as it seems to take some time for Google forms to auto populate this field
    page.wait_for_timeout(500)

    # ensure the form has the correct dataset name
    assert (
        page.get_by_role(
            "textbox", name="Which dataset were you looking at?"
        ).input_value()
        == "Brownfield site"
    )
