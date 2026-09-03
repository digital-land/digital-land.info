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


def add_provider(db_session, suffix, entity, is_designated_provider):
    name = f"Council {suffix}"
    db_session.add(
        OrganisationOrm(
            organisation=f"local-authority:{suffix}", name=name, entity=entity
        )
    )
    add_provision_quality(
        db_session,
        "greenspace",
        f"local-authority:{suffix}",
        name,
        is_designated_provider=is_designated_provider,
    )
    return name


def test_dataset_page_shows_providers_inline_when_five_or_fewer_exist(
    client, db_session, test_data, exclude_middleware
):
    """
    A mix of authoritative and alternative providers, totalling exactly 5 —
    the rule is a count threshold regardless of provider type.
    """
    entities = [600020, 600021, 600022, 600023, 600024]
    names = [
        add_provider(db_session, "A1", entities[0], is_designated_provider=True),
        add_provider(db_session, "A2", entities[1], is_designated_provider=True),
        add_provider(db_session, "B1", entities[2], is_designated_provider=False),
        add_provider(db_session, "B2", entities[3], is_designated_provider=False),
        add_provider(db_session, "B3", entities[4], is_designated_provider=False),
    ]
    db_session.flush()

    response = client.get("/dataset/greenspace")

    assert response.status_code == 200
    soup = BeautifulSoup(response.text, "html.parser")

    assert soup.find("a", href="/data-provider/greenspace") is None

    for entity, name in zip(entities, names):
        inline_link = soup.find("a", href=f"/entity/{entity}")
        assert inline_link is not None
        assert inline_link.get_text(strip=True) == name


def test_dataset_page_links_to_providers_when_more_than_five_exist(
    client, db_session, test_data, exclude_middleware
):
    for i in range(6):
        add_provider(
            db_session, f"C{i}", 600030 + i, is_designated_provider=(i % 2 == 0)
        )
    db_session.flush()

    response = client.get("/dataset/greenspace")

    assert response.status_code == 200
    soup = BeautifulSoup(response.text, "html.parser")
    provider_link = soup.find("a", href="/data-provider/greenspace")
    assert provider_link is not None
    assert provider_link.get_text(strip=True) == "6 data providers"


def test_dataset_page_shows_none_when_no_providers_at_all(
    client, db_session, test_data, exclude_middleware
):
    response = client.get("/dataset/greenspace")

    assert response.status_code == 200
    soup = BeautifulSoup(response.text, "html.parser")

    assert soup.find("a", href="/data-provider/greenspace") is None

    row_heading = soup.find(string="Data providers")
    row_value_cell = row_heading.find_parent("tr").find_all("td")[0]
    assert row_value_cell.get_text(strip=True) == "None"
