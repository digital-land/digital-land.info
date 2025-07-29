from tests.acceptance.pageObjectModels.mapPOM import MapPOM


def test_map_page_loads_ok(server_url, page):
    mapPage = MapPOM(page, server_url)
    mapPage.navigate()

    response = page.goto(server_url + "/map/")
    assert response.ok

    heading = page.get_by_role(
        "heading",
        name="Map of planning data for England",
    )
    assert heading.is_visible()

    banner = page.locator('#dl-data-coverage-banner')
    assert banner.is_visible()

    page.screenshot(path="playwright-report/test_map_page_loads_ok/map.png")


# def test_toggle_layers_on_the_national_map_correctly_shows_entity(
#     server_url,
#     page,
#     app_test_data,
#     skip_if_not_supportsGL,
#     test_settings,
# ):
#     # as the map xy coords are dependent on the viewport size, we need to set it to make sure the tests are consistent
#     mapPage = MapPOM(page, server_url)
#     mapPage.navigate("#50.88865897214836,-2.260771340418273,11.711391365982688z")
#     mapPage.check_layer_checkbox("Conservation area")
#     mapPage.wait_for_map_layer("conservation-area-source-fill-extrusion")


# the map doesn't seem to be properly loading on the cicd. so for now I'm going to put this test on hold

# def forwardLog(content, filename="playwright-report/log.txt"):
#     if not os.path.exists("playwright-report"):
#         os.makedirs("playwright-report")
#     with open(filename, "a+") as f:
#         current_time = time.strftime("%H:%M:%S", time.localtime())
#         f.write(current_time + ": " + content + "\n")


# def test_using_the_map_to_find_an_entity(
#     server_process,
#     page,
#     add_base_entities_to_database_yield_reset,
#     skip_if_not_supportsGL,
#     test_settings,
#     BASE_URL,
# ):

#     page.on("console", lambda msg: forwardLog(msg.text))

#     page.goto(BASE_URL)
#     page.get_by_role("link", name="Map", exact=True).click()

#     page.wait_for_timeout(1000)

#     mapPage = MapPOM(page, BASE_URL)

#     mapPage.wait_for_layer_controls_to_load()

#     mapPage.zoom_map(12)
#     mapPage.centre_map_over(-2.2294632745091576, 50.88634078931207)

#     mapPage.check_layer_checkbox("Conservation area")
#     mapPage.wait_for_map_layer("conservation-area-source-fill-extrusion")

#     page.wait_for_timeout(5000)

#     mapPage.click_map_centre()

#     page.screenshot(path="playwright-report/map.png")

#     mapPage.wait_for_popup()

#     with page.expect_navigation() as navigation_info:
#         page.get_by_role("link", name="1").click()

#     assert navigation_info.value.ok
#     assert page.url == BASE_URL + "/entity/44002322"

#     datasetHeading = page.locator("span").filter(has_text="Conservation area")
#     assert datasetHeading.is_visible()

#     ReferenceHeading = page.get_by_role(
#         "heading",
#         name="Historic England",
#     )
#     assert ReferenceHeading.is_visible()
