def test_guidance_pages_load_ok(server_url, page):
    response = page.goto(server_url + "/guidance")
    assert response.ok
    heading = page.get_by_role(
        "heading",
        name="Guidance for local planning authorities",
    ).last
    assert heading.is_visible()

    page.get_by_label("Guidance navigation").get_by_role(
        "link", name="Introduction"
    ).click()
    assert response.ok
    heading = page.get_by_role(
        "heading",
        name="Introduction for local planning authorities",
    )
    assert heading.is_visible()

    page.get_by_label("Guidance navigation").get_by_role(
        "link", name="How to provide data"
    ).click()
    assert response.ok
    heading = page.get_by_role(
        "heading",
        name="How to provide data",
    )
    assert heading.is_visible()

    page.get_by_label("Guidance navigation").get_by_role(
        "link", name="Data specifications guidance"
    ).click()
    assert response.ok
    heading = page.get_by_role(
        "heading",
        name="Data specifications for local planning authorities",
    )
    assert heading.is_visible()
