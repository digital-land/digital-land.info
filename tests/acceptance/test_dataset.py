import pytest

from playwright.sync_api._generated import Page


def test_dataset_page_loads_ok(server_url, page, app_test_data):
    response = page.goto(server_url + "/dataset/brownfield-site")
    assert response.ok
    heading = page.get_by_role(
        "heading",
        name="Brownfield site",
    )
    assert heading.is_visible()


def test_dataset_page_displays_conditional_warning_text(
    server_url: str, page: Page, app_test_data: dict[str, list]
):
    """
    Tests that the warning text displayed when viewing
    'Planning application' is different from when viewing
    all other datasets.
    """
    response = page.goto(server_url + "/dataset/planning-application")
    assert response.ok

    expected_warning_text = (
        "The planning application dataset is incomplete "
        "and is not yet ready for use. You can "
        "contribute to its development."
    )
    warning_text = page.get_by_text(
        "The planning application dataset is incomplete and is not yet ready for use."
    )

    assert warning_text.is_visible()
    actual_text = " ".join(warning_text.inner_text().split())
    # Remove "Warning" prefix from visually hidden span
    if actual_text.startswith("Warning "):
        actual_text = actual_text[8:]
    assert actual_text == expected_warning_text

    # Check that the warning message for a different dataset is different
    response = page.goto(server_url + "/dataset/brownfield-site")
    assert response.ok

    expected_warning_text = (
        "The data may be incomplete and not yet cover all "
        "of England. We're working to improve its "
        "availability and quality."
    )
    warning_text = page.get_by_text(
        "The data may be incomplete and not yet cover all of England."
    )

    assert warning_text.is_visible()
    actual_text = " ".join(warning_text.inner_text().split())
    # Remove "Warning" prefix from visually hidden span
    if actual_text.startswith("Warning "):
        actual_text = actual_text[8:]
    assert actual_text == expected_warning_text


@pytest.mark.skip(reason="Temporarily disablind. Playwright Issues")
def test_download_data_for_dataset(server_url, page, app_test_data):
    page.goto(server_url)

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


@pytest.mark.skip(reason="Temporarily disablind. Playwright Issues")
def test_navigate_to_a_dataset_specification(server_url, page, app_test_data):
    page.goto(server_url)
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


@pytest.mark.skip(reason="Temporarily disablind. Playwright Issues")
def test_give_feedback_on_a_dataset(server_url, page, app_test_data):
    page.goto(server_url)

    page.get_by_role("link", name="Datasets", exact=True).click()
    page.get_by_role("link", name="Geography").click()
    page.get_by_role("link", name="Brownfield site").click()
    linkHref = page.get_by_role(
        "link", name="Give feedback on this dataset"
    ).get_attribute("href")

    assert "forms.microsoft.com" in linkHref
    assert "Brownfield site" in linkHref


@pytest.mark.skip(reason="Temporarily disablind. Playwright Issues")
def test_datasets_correctly_show(server_url, page, app_test_data):
    page.goto(server_url)

    page.get_by_role("link", name="Datasets", exact=True).click()

    page.wait_for_timeout(200)  # wait for javascript to load

    listElements = page.locator("ol.dl-list-filter__list").locator("li >> a").all()

    assert len(listElements) == len(app_test_data["datasets"])

    datasets = [dataset["name"] for dataset in app_test_data["datasets"]]

    for element in listElements:
        assert element.text_content() in datasets, "dataset not in the list"
        datasets.remove(element.text_content())

    assert len(datasets) == 0, "there are still some datasets that are not in the list"


@pytest.mark.skip(reason="Temporarily disablind. Playwright Issues")
def test_list_filter_works_as_expected(server_url, page, app_test_data):
    timeout = 400
    page.goto(server_url)

    page.get_by_role("link", name="Datasets", exact=True).click()

    page.wait_for_timeout(timeout)  # wait for javascript to load

    page.locator("input.dl-list-filter__input").fill("o")
    page.wait_for_timeout(timeout)  # wait for javascript to load
    listElements = (
        page.locator("ol.dl-list-filter__list")
        .locator("li.dl-list-filter__item:not(.js-hidden) >> a")
        .all()
    )
    datasets = [
        dataset["name"]
        for dataset in app_test_data["datasets"]
        if "o" in dataset["name"]
    ]
    assert len(listElements) == len(datasets)

    page.locator("input.dl-list-filter__input").fill("on")
    page.wait_for_timeout(timeout)  # wait for javascript to load
    listElements = (
        page.locator("ol.dl-list-filter__list")
        .locator("li.dl-list-filter__item:not(.js-hidden) >> a")
        .all()
    )
    datasets = [
        dataset["name"]
        for dataset in app_test_data["datasets"]
        if "on" in dataset["name"]
    ]
    assert len(listElements) == len(datasets)

    page.locator("input.dl-list-filter__input").fill("brownfield")
    page.wait_for_timeout(timeout)  # wait for javascript to load
    listElements = (
        page.locator("ol.dl-list-filter__list")
        .locator("li.dl-list-filter__item:not(.js-hidden) >> a")
        .all()
    )
    datasets = [
        dataset["name"]
        for dataset in app_test_data["datasets"]
        if "brownfield" in dataset["name"].lower()
    ]
    assert len(listElements) == len(datasets)

    page.locator("input.dl-list-filter__input").fill("a string that wont find anything")
    page.wait_for_timeout(timeout)  # wait for javascript to load
    listElements = (
        page.locator("ol.dl-list-filter__list")
        .locator("li.dl-list-filter__item:not(.js-hidden) >> a")
        .all()
    )
    assert len(listElements) == 0
