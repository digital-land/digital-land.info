import pytest

from datetime import datetime

from application.db.models import TypologyOrm

from tests.acceptance.pageObjectModels.searchPOM import SearchPOM


def test_search_page_loads_ok(server_url, page):
    response = page.goto(server_url + "/entity/")
    assert response.ok
    heading = page.get_by_role(
        "heading",
        name="Search for planning and housing data",
    )
    assert heading.is_visible()


def test_blank_search(server_url, page):
    page.goto(server_url)
    page.click("text=Search")

    with page.expect_response("**/entity/**") as response:
        page.click("button:has-text(' Search ')")

    assert response.value.ok


@pytest.fixture
def app_typology_data():
    typologies = [
        {
            "typology": "geography",
            "name": "geography",
            "description": "This is an example typology.",
            "entry_date": "2022-01-01",
            "start_date": "2022-01-01",
            "end_date": "2022-12-31",
            "plural": "Example Typologies",
            "text": "This is some example text.",
            "wikidata": "Q12345",
            "wikipedia": "en:Example_Typology",
        },
        {
            "typology": "organisation",
            "name": "organisation",
            "description": "This is an example typology.",
            "entry_date": "2022-01-01",
            "start_date": "2022-01-01",
            "end_date": "2022-12-31",
            "plural": "Example Typologies",
            "text": "This is some example text.",
            "wikidata": "Q12345",
            "wikipedia": "en:Example_Typology",
        },
    ]
    return typologies


def test_search_filters_show_correct_number_of_results(
    server_url, page, app_test_data, app_db_session, app_typology_data
):
    for typology in app_typology_data:
        app_db_session.add(TypologyOrm(**typology))
    app_db_session.commit()

    page.goto(server_url)
    page.click("text=Search")

    page.wait_for_timeout(1000)

    searchPage = SearchPOM(page, server_url)

    # filter test data entities to only include organisations
    filtered = [
        entity
        for entity in app_test_data["entities"]
        if entity["typology"] == "organisation"
    ]

    searchPage.check_filter("typology", "organisation")
    searchPage.search_button_click()
    searchPage.test_count_of_results(len(filtered))

    # filter test data entities to include geographies and organisations
    filtered = [
        entity
        for entity in app_test_data["entities"]
        if entity["typology"] == "organisation" or entity["typology"] == "geography"
    ]

    searchPage.check_filter("typology", "geography")
    searchPage.search_button_click()
    searchPage.test_count_of_results(len(filtered))

    # filter test data entities to include typologies geographies and organisations and a dataset of brownfield sites
    filtered = [
        entity
        for entity in app_test_data["entities"]
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
        for entity in app_test_data["entities"]
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
        for entity in app_test_data["entities"]
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
        for entity in app_test_data["entities"]
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
