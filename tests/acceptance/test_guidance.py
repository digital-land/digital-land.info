from unittest.mock import patch, MagicMock
from application.routers.guidance_ import get_cms_content_item

def test_guidance_pages_load_ok(server_url, page):
    response = page.goto(server_url + "/guidance")
    assert response.ok
    heading = page.get_by_role(
        "heading",
        name="About the check and provide your planning data service",
    ).last
    assert heading.is_visible()

    page.get_by_label("Guidance navigation").get_by_role(
        "link", name="Prepare your data"
    ).click()
    assert response.ok
    heading = page.get_by_role(
        "heading",
        name="Prepare your data",
    )
    assert heading.is_visible()

    page.get_by_label("Guidance navigation").get_by_role(
        "link", name="Publish data on your website"
    ).click()
    assert response.ok
    heading = page.get_by_role(
        "heading",
        name="Publish data on your website",
    )
    assert heading.is_visible()

    page.get_by_label("Guidance navigation").get_by_role(
        "link", name="The Open Digital Planning community"
    ).click()
    assert response.ok
    heading = page.get_by_role(
        "heading",
        name="The Open Digital Planning community",
    )
    assert heading.is_visible()

    page.get_by_label("Guidance navigation").get_by_role(
        "link", name="Get help"
    ).click()
    assert response.ok
    heading = page.get_by_role(
        "heading",
        name="Get help",
    )
    assert heading.is_visible()


def test_get_cms_content_item_valid_path():
    url_path = "index"
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": {"title": "Test", "body": "Test body"}}
    with patch("application.routers.guidance_.get", return_value=mock_response):
        result = get_cms_content_item(url_path)
        assert result == {"data": {"title": "Test", "body": "Test body"}}


def test_get_cms_content_item_invalid_path():
    url_path = "non-existent"
    result = get_cms_content_item(url_path)
    assert result is None


def test_get_cms_content_item_exception_handling():
    url_path = "index"
    with patch("application.routers.guidance_.get", side_effect=Exception("API error")):
        result = get_cms_content_item(url_path)
        assert result is None
