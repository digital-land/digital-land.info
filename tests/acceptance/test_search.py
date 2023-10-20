from datetime import datetime
from tests.acceptance.pageObjectModels.searchPOM import SearchPOM


def test_search_page_loads_ok(server_process, BASE_URL, page):
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


def test_search_filters_show_correct_number_of_results(
    server_process, add_base_entities_to_database_yield_reset, test_data, BASE_URL, page
):
    page.goto(BASE_URL)
    page.click("text=Search")

    page.wait_for_timeout(1000)

    searchPage = SearchPOM(page, BASE_URL)

    # filter test data entities to only include organisations
    filtered = [
        entity
        for entity in test_data["entities"]
        if entity["typology"] == "organisation"
    ]

    searchPage.check_filter("typology", "organisation")
    searchPage.search_button_click()
    searchPage.test_count_of_results(len(filtered))

    # filter test data entities to include geographies and organisations
    filtered = [
        entity
        for entity in test_data["entities"]
        if entity["typology"] == "organisation" or entity["typology"] == "geography"
    ]

    searchPage.check_filter("typology", "geography")
    searchPage.search_button_click()
    searchPage.test_count_of_results(len(filtered))

    # filter test data entities to include typologies geographies and organisations and a dataset of brownfield sites
    filtered = [
        entity
        for entity in test_data["entities"]
        if (entity["typology"] == "organisation" or entity["typology"] == "geography")
        and entity["dataset"] == "brownfield-site"
    ]

    searchPage.check_filter("dataset", "Brownfield site")
    searchPage.search_button_click()
    searchPage.test_count_of_results(len(filtered))

    # filter test data entities to include typologies geographies and organisations
    # and a dataset of brownfield sites and an end date that is in the past
    filtered = [
        entity
        for entity in test_data["entities"]
        if (entity["typology"] == "organisation" or entity["typology"] == "geography")
        and (entity["dataset"] == "brownfield-site")
        and (
            entity["end_date"] is not None
            and datetime.strptime(entity["end_date"], "%Y-%m-%d") < datetime.now()
        )
    ]

    searchPage.check_filter("period", "Historical")
    searchPage.search_button_click()
    searchPage.test_count_of_results(len(filtered))

    # clear all filters bar historical and check that the number of results is correct
    filtered = [
        entity
        for entity in test_data["entities"]
        if (
            entity["end_date"] is not None
            and datetime.strptime(entity["end_date"], "%Y-%m-%d") < datetime.now()
        )
    ]

    searchPage.clear_filter("geography")
    searchPage.clear_filter("organisation")
    searchPage.clear_filter("brownfield-site")
    searchPage.search_button_click()
    searchPage.test_count_of_results(len(filtered))

    # clear remaining filters, and filter by entry date
    filtered = [
        entity
        for entity in test_data["entities"]
        if (
            entity["entry_date"] is not None
            and datetime.strptime(entity["entry_date"], "%Y-%m-%d")
            < datetime.strptime("2020-09-04", "%Y-%m-%d")
        )
    ]

    searchPage.clear_filter("historical")
    searchPage.filter_by_entry_date("before", "2020", "09", "04")
    searchPage.search_button_click()
    searchPage.test_count_of_results(len(filtered))
