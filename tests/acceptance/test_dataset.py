def test_roadmap_loads_ok(server_process, BASE_URL, page):
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
