from tests.acceptance.pageObjectModels.mapPOM import MapPOM


def test_map_page_loads_ok(server_process, BASE_URL, page):
    mapPage = MapPOM(page, BASE_URL)
    mapPage.navigate()
    response = page.goto(BASE_URL + "/map/")
    assert response.ok
    heading = page.get_by_role(
        "heading",
        name="Map of planning data for England",
    )
    assert heading.is_visible()


def test_toggle_layers_on_the_national_map_correctly_shows_entity(
    server_process,
    page,
    add_base_entities_to_database_yield_reset,
    skip_if_not_supportsGL,
    test_settings,
    BASE_URL,
):
    # as the map xy coords are dependent on the viewport size, we need to set it to make sure the tests are consistent
    mapPage = MapPOM(page, BASE_URL)
    mapPage.navigate("#50.88865897214836,-2.260771340418273,11.711391365982688z")
    mapPage.check_layer_checkbox("Conservation area")
    mapPage.wait_for_map_layer("conservation-area-source-fill-extrusion")


def test_using_the_map_to_find_an_entity(
    server_process,
    page,
    add_base_entities_to_database_yield_reset,
    skip_if_not_supportsGL,
    test_settings,
    BASE_URL,
):
    page.goto(BASE_URL)
    page.get_by_role("link", name="Map", exact=True).click()

    mapPage = MapPOM(page, BASE_URL)

    mapPage.check_layer_checkbox("Conservation area")
    mapPage.wait_for_map_layer("conservation-area-source-fill-extrusion")

    mapPage.zoom_map(12)
    mapPage.centre_map_over(-2.2294632745091576, 50.88634078931207)
    mapPage.click_map_centre()

    with page.expect_navigation() as navigation_info:
        page.get_by_role("link", name="1").click()

    assert navigation_info.value.ok
    assert page.url == BASE_URL + "/entity/44002322"

    datasetHeading = page.locator("span").filter(has_text="Conservation area")
    assert datasetHeading.is_visible()

    ReferenceHeading = page.get_by_role(
        "heading",
        name="Historic England",
    )
    assert ReferenceHeading.is_visible()
