def test_guidance_pages_load_ok(server_url, page):
    response = page.goto(server_url + "/guidance")
    assert response.ok
    heading = page.get_by_role(
        "heading",
        name="Provide planning and housing data for England",
    ).last
    assert heading.is_visible()

    page.get_by_label("Guidance navigation").get_by_role(
        "link", name="Prepare data to the specifications"
    ).click()
    assert response.ok
    heading = page.get_by_role(
        "heading",
        name="Prepare data to the specifications",
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
        "link", name="Keep your data up to date"
    ).click()
    assert response.ok
    heading = page.get_by_role(
        "heading",
        name="Keep your data up to date",
    )
    assert heading.is_visible()

    page.get_by_label("Guidance navigation").get_by_role(
        "link", name="Try our new check and publish service"
    ).click()
    assert response.ok
    heading = page.get_by_role(
        "heading",
        name="Try our new check and publish service",
    )
    assert heading.is_visible()
