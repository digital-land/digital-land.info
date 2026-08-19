def test_primary_navigation_subnav_focus_order(server_url, page):
    """
    Expanding a primary nav item's sub-nav inserts it into the tab
    sequence immediately after the toggle, so the next tab stop is
    inside the sub-menu, not the next primary nav item.
    """
    page.goto(server_url)

    nav_with_subnav = page.locator(".govuk-service-navigation__item").filter(
        has=page.get_by_role("button", name="Data", exact=True)
    )
    toggle = nav_with_subnav.get_by_role("button", name="Data", exact=True)
    subnav = nav_with_subnav.locator(".dl-subnav")

    toggle.focus()
    page.keyboard.press("Enter")
    assert toggle.get_attribute("aria-expanded") == "true"

    page.keyboard.press("Tab")
    assert subnav.locator(":focus").count() == 1
