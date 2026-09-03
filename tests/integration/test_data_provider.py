from bs4 import BeautifulSoup

from application.db.models import OrganisationOrm, ProvisionQualityOrm


def add_provision_quality(
    db_session,
    dataset,
    organisation,
    organisation_name,
    is_designated_provider,
):
    db_session.add(
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


def test_provider_page_groups_providers_by_authoritative_and_alternative(
    client, db_session, test_data, exclude_middleware
):
    db_session.add(
        OrganisationOrm(
            organisation="local-authority:AUTH",
            name="Authoritative Council",
            entity=600001,
        )
    )
    db_session.add(
        OrganisationOrm(
            organisation="local-authority:ALT",
            name="Alternative Council",
            entity=600002,
        )
    )
    add_provision_quality(
        db_session,
        "greenspace",
        "local-authority:AUTH",
        "Authoritative Council",
        is_designated_provider=True,
    )
    add_provision_quality(
        db_session,
        "greenspace",
        "local-authority:ALT",
        "Alternative Council",
        is_designated_provider=False,
    )
    db_session.flush()

    response = client.get("/data-provider/greenspace")

    assert response.status_code == 200
    soup = BeautifulSoup(response.text, "html.parser")

    authoritative_section = soup.find(id="authoritative-sources").find_parent(
        class_="dl-list-filter__count"
    )
    alternative_section = soup.find(id="alternative-sources").find_parent(
        class_="dl-list-filter__count"
    )

    authoritative_link = authoritative_section.find("a", href="/entity/600001")
    assert authoritative_link is not None
    assert authoritative_link.get_text(strip=True) == "Authoritative Council"

    alternative_link = alternative_section.find("a", href="/entity/600002")
    assert alternative_link is not None
    assert alternative_link.get_text(strip=True) == "Alternative Council"

    # Confirm each provider only appears in its own section
    assert authoritative_section.find("a", href="/entity/600002") is None
    assert alternative_section.find("a", href="/entity/600001") is None


def test_provider_page_returns_404_for_unknown_dataset(
    client, db_session, test_data, exclude_middleware
):
    response = client.get("/data-provider/not-a-real-dataset")

    assert response.status_code == 404


def test_provider_page_hides_heading_for_empty_group(
    client, db_session, test_data, exclude_middleware
):
    db_session.add(
        OrganisationOrm(
            organisation="local-authority:AUTH",
            name="Authoritative Council",
            entity=600003,
        )
    )
    add_provision_quality(
        db_session,
        "greenspace",
        "local-authority:AUTH",
        "Authoritative Council",
        is_designated_provider=True,
    )
    db_session.flush()

    response = client.get("/data-provider/greenspace")

    assert response.status_code == 200
    soup = BeautifulSoup(response.text, "html.parser")

    assert soup.find(id="authoritative-sources") is not None
    assert soup.find(id="alternative-sources") is None


def test_provider_page_shows_intro_text_with_dynamic_dataset_name(
    client, db_session, test_data, exclude_middleware
):
    response = client.get("/data-provider/greenspace")

    assert response.status_code == 200
    assert (
        "These sources provide the data used in the Greenspace dataset."
        in response.text
    )


def test_provider_page_no_match_message_includes_dataset_name(
    client, db_session, test_data, exclude_middleware
):
    response = client.get("/data-provider/greenspace")

    assert response.status_code == 200
    assert "No data provider for Greenspace matches" in response.text


def test_provider_page_shows_visible_empty_state_when_no_providers_exist(
    client, db_session, test_data, exclude_middleware
):
    response = client.get("/data-provider/greenspace")

    assert response.status_code == 200
    soup = BeautifulSoup(response.text, "html.parser")

    empty_state = soup.find(
        "p",
        string=lambda text: text and "no known data providers" in text.lower(),
    )
    assert empty_state is not None
    assert "Greenspace" in empty_state.get_text()
    # This message must be visible by default, unlike the JS-only no-match
    # message which only appears after a search yields nothing.
    assert empty_state.find_parent(class_="js-hidden") is None
