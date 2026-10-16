from datetime import date

from bs4 import BeautifulSoup

from application.db.models import ProvisionQualityOrm


def add_provision_quality(
    db_session,
    dataset="greenspace",
    organisation="local-authority:X",
    start_date=date(2024, 1, 1),
    quality="authoritative",
):
    db_session.add(
        ProvisionQualityOrm(
            dataset=dataset,
            organisation=organisation,
            organisation_name="Test Council",
            has_active_endpoint=True,
            has_active_resource=True,
            owns_entities=True,
            is_designated_provider=True,
            quality=quality,
            entity_count=10,
            quality_score=None,
            start_date=start_date,
        )
    )


def test_performance_page_shows_counts_and_change_since_last_year(client, db_session):
    today = date.today()
    add_provision_quality(
        db_session,
        dataset="greenspace",
        organisation="local-authority:X",
        start_date=today.replace(year=today.year - 3),
    )
    add_provision_quality(
        db_session,
        dataset="conservation-area",
        organisation="local-authority:Y",
        start_date=today.replace(day=1),
    )
    db_session.flush()

    response = client.get("/about/performance")
    assert response.status_code == 200

    soup = BeautifulSoup(response.content, "html.parser")
    content = soup.find(id="content_primary")
    headings = [h2.get_text(strip=True) for h2 in content.find_all("h2")]
    assert headings == [
        "Who provides data",
        "Checking data quality",
        "Data across England",
    ]

    stat_values = [
        el.get_text(strip=True) for el in soup.select(".app-headline-count__value")
    ]
    assert stat_values == ["2", "2"]

    changes = [
        el.get_text(strip=True) for el in soup.select(".app-headline-count__change")
    ]
    assert any("1 since last count" in c for c in changes)


def test_performance_page_shows_no_change_when_nobody_new_has_published(
    client, db_session
):
    add_provision_quality(
        db_session,
        start_date=date(2020, 1, 1),
    )
    db_session.flush()

    response = client.get("/about/performance")
    assert response.status_code == 200

    soup = BeautifulSoup(response.content, "html.parser")
    changes = [
        el.get_text(strip=True) for el in soup.select(".app-headline-count__change")
    ]
    assert all("No change since last count" in c for c in changes)


def test_performance_page_shows_authoritative_and_alternative_source_breakdown(
    client, db_session
):
    add_provision_quality(
        db_session, organisation="local-authority:X", quality="authoritative"
    )
    add_provision_quality(db_session, organisation="local-authority:Y", quality="some")
    db_session.flush()

    response = client.get("/about/performance")
    assert response.status_code == 200

    soup = BeautifulSoup(response.content, "html.parser")
    items = [li.get_text(strip=True) for li in soup.select(".govuk-list--bullet li")]
    assert "1 authoritative sources" in items
    assert "1 alternative sources" in items


def test_performance_page_hides_source_breakdown_when_no_providers_exist(
    client, db_session
):
    response = client.get("/about/performance")
    assert response.status_code == 200

    soup = BeautifulSoup(response.content, "html.parser")
    assert soup.find(string="Data providers are currently made up of:") is None
    assert soup.select(".govuk-list--bullet li") == []

    # the rest of the page still renders, honestly reporting zero
    stat_values = [
        el.get_text(strip=True) for el in soup.select(".app-headline-count__value")
    ]
    assert stat_values == ["0", "0"]
