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
