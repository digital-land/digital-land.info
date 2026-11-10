from unittest.mock import MagicMock, patch

import pytest
from bs4 import BeautifulSoup

from application.core.models import FactModel
from application.routers.fact import get_fact
from application.search.filters import FactDatasetQueryFilters, FactPathParams

FACT_HASH = "180b185fbe277e7ae6d0da63b57eb46549d21fd6424e9890c4cd73f9490dde93"


def _render_fact_page(db_session, value):
    fact = FactModel(
        fact=FACT_HASH,
        entity=1,
        field="website",
        value=value,
        entity_name="Green space",
        resources='[{"resource":"abc123","entry_date":"2022-03-23"}]',
    )
    with patch(
        "application.search.validators.get_dataset_names",
        return_value=["greenspace"],
    ):
        query_filters = FactDatasetQueryFilters(dataset="greenspace")

    # get_fact_query calls datasette, so return the fact directly.
    with patch("application.routers.fact.get_fact_query", return_value=fact):
        response = get_fact(
            request=MagicMock(),
            path_params=FactPathParams(fact=FACT_HASH),
            query_filters=query_filters,
            extension=None,
            session=db_session,
        )
    assert response.status_code == 200
    return BeautifulSoup(response.body, "html.parser")


def test_get_fact_does_not_link_unsafe_website(db_session, test_data):
    soup = _render_fact_page(db_session, "javascript:alert(1)")

    hrefs = [a["href"] for a in soup.find_all("a", href=True)]
    assert not [h for h in hrefs if h.strip().lower().startswith("javascript:")]
    assert "javascript:alert(1)" in soup.get_text()


@pytest.mark.parametrize("url", ["https://example.com/ok", "http://example.com/ok"])
def test_get_fact_still_links_safe_website(db_session, test_data, url):
    soup = _render_fact_page(db_session, url)
    assert soup.find("a", href=url) is not None
