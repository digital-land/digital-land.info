from dl_web.core.filters import render_markdown


def test_render_markdown_returns_govuk_styled_paragraphs():
    expected = '<p class="govuk-body">This is a paragraph</p>'
    actual = render_markdown("This is a paragraph")
    assert actual == expected
