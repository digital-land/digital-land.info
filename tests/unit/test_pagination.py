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
