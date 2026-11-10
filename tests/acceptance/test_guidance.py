from urllib.parse import quote


def test_guidance_pages_load_ok(server_url, page):
    response = page.goto(server_url + "/guidance")
    assert response.ok
    # assert the main guidance heading is visible
    heading = page.get_by_role("heading", name="Guidance", exact=True)
    assert heading.is_visible(timeout=5000)  # 5 second timeout

    # Prepare your data
    page.get_by_label("Guidance navigation").get_by_role(
        "link", name="Prepare your data"
    ).click()
    assert response.ok
    heading = page.get_by_role(
        "heading",
        name="Prepare your data",
    )
    assert heading.is_visible()

    # Check your data
    page.get_by_label("Guidance navigation").get_by_role(
        "link", name="Check your data"
    ).click()
    assert response.ok
    heading = page.get_by_role(
        "heading",
        name="Check your data",
    )
    assert heading.is_visible()

    # Publish your data
    page.get_by_label("Guidance navigation").get_by_role(
        "link", name="Publish your data"
    ).click()
    assert response.ok
    heading = page.get_by_role(
        "heading",
        name="Publish your data",
    )
    assert heading.is_visible()

    # Provide your data
    page.get_by_label("Guidance navigation").get_by_role(
        "link", name="Provide your data"
    ).click()
    assert response.ok
    heading = page.get_by_role(
        "heading",
        name="Provide your data",
        exact=True,
    )
    assert heading.is_visible()

    # View your data
    page.get_by_label("Guidance navigation").get_by_role(
        "link", name="View your data"
    ).click()
    assert response.ok
    heading = page.get_by_role(
        "heading",
        name="View your data",
    )
    assert heading.is_visible()

    # Update your data
    page.get_by_label("Guidance navigation").get_by_role(
        "link", name="Update your data"
    ).click()
    assert response.ok
    heading = page.get_by_role(
        "heading",
        name="Update your data",
    )
    assert heading.is_visible()


def test_finder_example_shows_url_filters_as_text(server_url, page):
    """Values from the finder's query string are shown as text in the filter
    chips and never run as HTML."""
    payload = '<img src=x onerror="window.__xss=1">'
    dialogs = []
    page.on("dialog", lambda dialog: (dialogs.append(dialog), dialog.dismiss()))

    page.goto(
        server_url
        + "/guidance/publish-data-on-your-website/examples/finder"
        + f"?q={quote(payload)}&type={quote(payload)}"
    )

    chips = page.locator("#active-filters-row")
    chips.locator(".filter-chip").first.wait_for()

    assert chips.locator("img").count() == 0
    assert payload in chips.inner_text()
    assert page.evaluate("window.__xss") is None
    assert dialogs == []
