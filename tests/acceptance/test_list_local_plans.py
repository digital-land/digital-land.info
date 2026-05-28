import pytest


def test_list_local_plans_loads_ok(server_url, page):
    response = page.goto(server_url + "/local-plans/")
    assert response.ok

    heading = page.get_by_role(
        "heading",
        name="Local plans",
    )
    assert heading.is_visible()

    page_intro_paragraph = page.locator(".govuk-body-l").first
    assert page_intro_paragraph.is_visible()


@pytest.mark.parametrize(
    "query, expected_datasets_name",
    [
        (
            "?dataset=local-plan",
            ["Local plan"],
        ),
        (
            "?dataset=local-plan&dataset=local-plan-boundary",
            ["Local plan", "Local plan boundary"],
        ),
    ],
)
def test_list_local_plans_query_filter_html(
    server_url, page, app_test_data, query, expected_datasets_name
):
    url = f"{server_url}/local-plans/{query}"
    response = page.goto(url)
    assert response.ok

    page_content = page.content()
    assert "local-plan" in page_content

    list_datasets = page.locator(".dl-list-filter__item a").all()
    dataset_names_on_page = [ld.text_content().strip() for ld in list_datasets]

    for expected in expected_datasets_name:
        assert expected in dataset_names_on_page


@pytest.mark.parametrize(
    "query, expected_datasets, expected_fields",
    [
        (
            "?dataset=local-plan&field=dataset&field=name",
            ["local-plan"],
            ["dataset", "name"],
        ),
        (
            "?dataset=local-plan-boundary&include_typologies=false",
            ["local-plan-boundary"],
            None,
        ),
    ],
)
def test_list_local_plans_query_filter_json(
    server_url,
    page,
    query,
    app_test_data,
    expected_datasets,
    expected_fields,
):
    url = f"{server_url}/local-plans.json{query}"
    response = page.goto(url)
    assert response.ok

    data = response.json()
    returned_datasets = [ds["dataset"] for ds in data["datasets"]]
    assert returned_datasets == expected_datasets

    if expected_fields:
        for ds in data["datasets"]:
            for field in expected_fields:
                assert field in ds

    assert not data.get("typologies")
