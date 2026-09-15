import re

from bs4 import BeautifulSoup


def test_dataset_index_page_exposes_filter_result_count_as_a_status_message(
    client, db_session, test_data, exclude_middleware
):
    """
    WCAG 4.1.3 Status Messages: filtering the dataset list updates a
    visually-hidden result count via JavaScript, but a screen reader only
    announces that change if the count lives inside a role="status" live
    region. Without it, filtering silently changes the results with no
    indication to screen reader users that anything happened.

    This checks the server-rendered markup carries that wiring on initial
    load — the dynamic wording update itself is covered by the JS unit
    test in tests/unit/javascript/ListFilter.test.js.

    Not duplicated for organisation_index.html / data_provider_index.html:
    they render the exact same list-filter markup, JS, and `pluralize`
    filter, so this one test already covers all three. If either page's
    filter ever diverges from this shared pattern, give it its own test.
    """
    response = client.get("/dataset/")
    assert response.status_code == 200

    soup = BeautifulSoup(response.text, "html.parser")
    status_messages = soup.select(".dl-list-filter__count__wrapper p")

    assert status_messages, "expected at least one list-filter result count on the page"
    for status in status_messages:
        assert status.get("role") == "status"
        assert re.search(r"\d", status.get_text())
