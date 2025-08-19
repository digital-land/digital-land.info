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
    "query, expected_datasets, expected_fields, exclude_typologies",
    [
        (
            "?dataset=brownfield-site",
            ["brownfield-site"],
            None,
            False,
        ),  # all data for just one dataset
        (
            "?dataset=brownfield-site&dataset=conservation-area",
            ["brownfield-site", "conservation-area"],
            None,
            False,
        ),  # all data for just two dataset
    ],
)
def test_list_datasets_query_filter_html(
    server_url, page, query, expected_datasets, expected_fields, exclude_typologies
):
    url = f"{server_url}/dataset/{query}"
    response = page.goto(url)
    assert response.ok

    page_content = page.content()
    assert "dataset" in page_content


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
    server_url, page, query, expected_datasets, expected_fields, exclude_typologies
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
