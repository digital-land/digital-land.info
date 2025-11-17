import pytest


def test_dataset_index_loads_ok(server_url, page):
    response = page.goto(server_url + "/dataset/")
    assert response.ok

    heading = page.get_by_role(
        "heading",
        name="Datasets",
    )
    assert heading.is_visible()

    banner = page.locator("#dl-data-coverage-banner")
    assert banner.is_visible()


@pytest.mark.parametrize(
    "query, expected_datasets_name",
    [
        (
            "?dataset=brownfield-site",
            ["Brownfield site"],
        ),  # all data for just one dataset
        (
            "?dataset=brownfield-site&dataset=conservation-area",
            ["Brownfield site", "Conservation area"],
        ),  # all data for just two dataset
    ],
)
def test_list_datasets_query_filter_html(
    server_url, page, app_test_data, query, expected_datasets_name
):
    url = f"{server_url}/dataset/{query}"
    response = page.goto(url)
    assert response.ok

    page_content = page.content()

    assert "dataset" in page_content
    list_datasets = page.locator("ol.dl-list-filter__list li a").all()
    dataset_names_on_page = [ld.text_content().strip() for ld in list_datasets]

    for expected in expected_datasets_name:
        assert expected in dataset_names_on_page


@pytest.mark.parametrize(
    "query, expected_datasets, expected_fields, exclude_typologies",
    [
        (
            "?dataset=conservation-area&field=dataset&field=name",
            ["conservation-area"],
            ["dataset", "name"],
            True,
        ),
        (
            "?dataset=conservation-area&include_typologies=false",
            ["conservation-area"],
            None,
            False,
        ),
    ],
)
def test_list_datasets_query_filter_json(
    server_url,
    page,
    query,
    app_test_data,
    expected_datasets,
    expected_fields,
    exclude_typologies,
):
    url = f"{server_url}/dataset.json{query}"
    response = page.goto(url)
    assert response.ok
    data = response.json()
    returned_datasets = [ds["dataset"] for ds in data["datasets"]]
    assert returned_datasets == expected_datasets
    if expected_fields:
        for ds in data["datasets"]:
            for field in expected_fields:
                assert field in ds

    if exclude_typologies:
        assert data.get("typologies") is not None
    else:
        assert not data.get("typologies")
