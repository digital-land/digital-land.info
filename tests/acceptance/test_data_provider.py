import re

from playwright.sync_api import expect

from application.db.models import EntityOrm, OrganisationOrm, ProvisionQualityOrm


def add_organisation(app_db_session, organisation, name, entity):
    app_db_session.add(
        OrganisationOrm(organisation=organisation, name=name, entity=entity)
    )
    app_db_session.add(
        EntityOrm(
            entity=entity,
            name=name,
            dataset="local-authority",
            typology="organisation",
            prefix="local-authority",
            reference=organisation.split(":")[-1],
        )
    )


def add_provision_quality(
    app_db_session,
    dataset,
    organisation,
    organisation_name,
    is_designated_provider,
):
    app_db_session.add(
        ProvisionQualityOrm(
            dataset=dataset,
            organisation=organisation,
            organisation_name=organisation_name,
            has_active_endpoint=True,
            has_active_resource=True,
            owns_entities=True,
            is_designated_provider=is_designated_provider,
            quality="authoritative" if is_designated_provider else "some",
            entity_count=10,
            quality_score=None,
        )
    )


def test_data_provider_page_loads_ok(server_url, page, app_test_data, app_db_session):
    add_organisation(
        app_db_session, "local-authority:ACC-TEST", "Acceptance Test Council", 700001
    )
    add_provision_quality(
        app_db_session,
        "brownfield-site",
        "local-authority:ACC-TEST",
        "Acceptance Test Council",
        is_designated_provider=True,
    )
    app_db_session.commit()

    response = page.goto(server_url + "/data-provider/brownfield-site")
    assert response.ok

    heading = page.get_by_role("heading", name="Data providers")
    assert heading.is_visible()

    provider_link = page.get_by_role("link", name="Acceptance Test Council")
    assert provider_link.is_visible()


def test_navigate_to_data_provider_page_and_through_to_organisation(
    server_url, page, app_test_data, app_db_session
):
    # The dataset page only links to the data providers page once there are
    # more than 5 providers — 5 or fewer are shown inline instead. Seed extra
    # filler providers so the link this test is exercising actually renders.
    for i in range(5):
        add_organisation(
            app_db_session,
            f"local-authority:ACC-FILLER{i}",
            f"Filler Council {i}",
            700010 + i,
        )
        add_provision_quality(
            app_db_session,
            "brownfield-site",
            f"local-authority:ACC-FILLER{i}",
            f"Filler Council {i}",
            is_designated_provider=True,
        )

    add_organisation(
        app_db_session, "local-authority:ACC-NAV", "Navigation Test Council", 700002
    )
    add_provision_quality(
        app_db_session,
        "brownfield-site",
        "local-authority:ACC-NAV",
        "Navigation Test Council",
        is_designated_provider=True,
    )
    app_db_session.commit()

    page.goto(server_url + "/dataset/brownfield-site")

    provider_link = page.get_by_role("link", name="6 data providers")
    with page.expect_navigation() as navigation_info:
        provider_link.click()

    assert navigation_info.value.ok
    assert server_url + "/data-provider/brownfield-site" in navigation_info.value.url

    heading = page.get_by_role("heading", name="Data providers")
    assert heading.is_visible()

    org_link = page.get_by_role("link", name="Navigation Test Council")
    with page.expect_navigation() as org_navigation:
        org_link.click()

    assert org_navigation.value.ok
    assert "/entity/700002" in org_navigation.value.url


def test_data_provider_list_filter_works_as_expected(
    server_url, page, app_test_data, app_db_session
):
    add_organisation(
        app_db_session, "local-authority:ACC-A", "Aardvark Council", 700003
    )
    add_organisation(app_db_session, "local-authority:ACC-Z", "Zebra Council", 700004)
    add_provision_quality(
        app_db_session,
        "brownfield-site",
        "local-authority:ACC-A",
        "Aardvark Council",
        is_designated_provider=True,
    )
    add_provision_quality(
        app_db_session,
        "brownfield-site",
        "local-authority:ACC-Z",
        "Zebra Council",
        is_designated_provider=True,
    )
    app_db_session.commit()

    page.goto(server_url + "/data-provider/brownfield-site")

    filter_form = page.locator("form[data-module='dl-list-filter-form']")
    expect(filter_form).to_have_class(re.compile(r"list-filter__form--active"))

    filter_input = page.locator("input.dl-list-filter__input")
    visible_items = page.locator("li.dl-list-filter__item:not(.js-hidden) >> a")

    filter_input.fill("Aardvark")
    expect(visible_items).to_have_count(1)
    assert visible_items.all()[0].text_content() == "Aardvark Council"

    filter_input.fill("a string that wont find anything")
    expect(visible_items).to_have_count(0)

    no_match_message = page.locator(".dl-list-filter__no-filter-match")
    expect(no_match_message).to_be_visible()
