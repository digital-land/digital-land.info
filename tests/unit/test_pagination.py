import pytest
from application.core.utils import make_links

scheme = "http"
netloc = "localhost"
path = "/entity.json"


def test_pagination_links_should_be_empty_if_no_results():
    data = {"count": 0, "params": {"limit": 10}}
    params = {}
    links = make_links(scheme, netloc, path, params, data)
    assert links == {}


def test_pagination_links_should_be_empty_if_count_results_less_than_limit():
    data = {"count": 1, "params": {"limit": 10}}
    params = {}
    links = make_links(scheme, netloc, path, params, data)
    assert links == {}

    data = {"count": 10, "params": {"limit": 10}}
    params = {}
    links = make_links(scheme, netloc, path, params, data)
    assert links == {}


def test_pagination_links_should_have_all_links_except_previous_on_first_page():
    data = {"count": 11, "params": {"limit": 10}}
    params = {}
    links = make_links(scheme, netloc, path, params, data)

    assert links["first"] == "http://localhost/entity.json?limit=10"
    assert links["next"] == "http://localhost/entity.json?limit=10&offset=10"
    assert links["last"] == "http://localhost/entity.json?limit=10&offset=10"
    assert links.get("prev") is None

    data = {"count": 20, "params": {"limit": 10}}
    params = {}
    links = make_links(scheme, netloc, path, params, data)

    assert links["first"] == "http://localhost/entity.json?limit=10"
    assert links["next"] == "http://localhost/entity.json?limit=10&offset=10"
    assert links["last"] == "http://localhost/entity.json?limit=10&offset=20"
    assert links.get("prev") is None


def test_pagination_links_should_have_previous_link_if_not_on_last_page():
    data = {"count": 45, "params": {"limit": 10, "offset": 10}}
    params = {}
    links = make_links(scheme, netloc, path, params, data)
    assert links["first"] == "http://localhost/entity.json?limit=10"
    assert links["prev"] == "http://localhost/entity.json?limit=10"
    assert links["next"] == "http://localhost/entity.json?limit=10&offset=20"
    assert links["last"] == "http://localhost/entity.json?limit=10&offset=40"

    data = {"count": 45, "params": {"limit": 10, "offset": 20}}
    params = {}
    links = make_links(scheme, netloc, path, params, data)
    assert links["first"] == "http://localhost/entity.json?limit=10"
    assert links["prev"] == "http://localhost/entity.json?limit=10&offset=10"
    assert links["next"] == "http://localhost/entity.json?limit=10&offset=30"
    assert links["last"] == "http://localhost/entity.json?limit=10&offset=40"

    data = {"count": 45, "params": {"limit": 10, "offset": 30}}
    params = {}
    links = make_links(scheme, netloc, path, params, data)
    assert links["first"] == "http://localhost/entity.json?limit=10"
    assert links["prev"] == "http://localhost/entity.json?limit=10&offset=20"
    assert links["next"] == "http://localhost/entity.json?limit=10&offset=40"
    assert links["last"] == "http://localhost/entity.json?limit=10&offset=40"

    data = {"count": 45, "params": {"limit": 10, "offset": 40}}
    params = {}
    links = make_links(scheme, netloc, path, params, data)
    assert links["first"] == "http://localhost/entity.json?limit=10"
    assert links["prev"] == "http://localhost/entity.json?limit=10&offset=30"
    assert links["last"] == "http://localhost/entity.json?limit=10&offset=40"


def test_pagination_links_should_not_have_next_link_on_last_page():
    data = {"count": 45, "params": {"limit": 10, "offset": 40}}
    params = {}
    links = make_links(scheme, netloc, path, params, data)
    assert links.get("next") is None


def test_pagination_if_limit_zero_then_no_links():
    data = {"count": 100, "params": {"limit": 0}}
    params = {}
    links = make_links(scheme, netloc, path, params, data)
    assert links == {}


def test_capped_first_page_has_no_links():
    data = {
        "count": 10_000,
        "count_is_capped": True,
        "pagination_is_capped": True,
        "params": {"limit": 10, "offset": 0},
    }
    assert make_links(scheme, netloc, path, "limit=10", data) == {}


def test_capped_later_page_only_links_back_to_first_page():
    data = {
        "count": 10_000,
        "count_is_capped": True,
        "pagination_is_capped": True,
        "params": {"limit": 10, "offset": 10},
    }
    links = make_links(scheme, netloc, path, "limit=10&offset=10", data)
    assert list(links) == ["first"]
    assert "offset" not in links["first"]


def test_count_exactly_at_the_cap_keeps_normal_pagination():
    data = {
        "count": 10_000,
        "count_is_capped": False,
        "params": {"limit": 10, "offset": 0},
    }
    links = make_links(scheme, netloc, path, "limit=10", data)
    assert "next" in links and "last" in links


@pytest.mark.parametrize(
    "offset, has_next_page, expected_links",
    [
        (0, True, ["first", "next"]),
        (10, True, ["first", "prev", "next"]),
        (20_000, False, ["first", "prev"]),
    ],
)
def test_capped_count_keeps_pagination_without_a_last_page(
    offset, has_next_page, expected_links
):
    data = {
        "count": 10_000,
        "count_is_capped": True,
        "has_next_page": has_next_page,
        "params": {"limit": 10, "offset": offset},
    }
    links = make_links(scheme, netloc, path, f"limit=10&offset={offset}", data)
    assert list(links) == expected_links
    if "next" in links:
        assert f"offset={offset + 10}" in links["next"]


def test_page_beyond_browse_limit_only_links_back_to_first_page():
    data = {
        "count": 10_000,
        "count_is_capped": True,
        "beyond_browse_limit": True,
        "has_next_page": False,
        "params": {"limit": 10, "offset": 10_000},
    }
    links = make_links(scheme, netloc, path, "limit=10&offset=10000", data)
    assert list(links) == ["first"]
    assert "offset" not in links["first"]
