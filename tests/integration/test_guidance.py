import asyncio
import re
from unittest.mock import MagicMock

from bs4 import BeautifulSoup

from application.routers.guidance_ import catch_all

FINDER_PATH = "publish-data-on-your-website/examples/finder"


def _render_guidance_page(url_path):
    response = asyncio.run(catch_all(request=MagicMock(), url_path=url_path))
    assert response.status_code == 200
    return BeautifulSoup(response.body, "html.parser")


def _render_chips_source(soup):
    script = next(
        (
            s.string
            for s in soup.find_all("script")
            if s.string and "renderChips" in s.string
        ),
        None,
    )
    assert script is not None, "finder script not found"
    match = re.search(r"function renderChips\(params\) \{.*?\n\}", script, re.S)
    assert match is not None, "renderChips function not found"
    return match.group(0)


def test_finder_example_builds_filter_chips_without_innerhtml():
    """Filter chip labels come from the URL query string, so they must be
    written as text, never as HTML."""
    render_chips = _render_chips_source(_render_guidance_page(FINDER_PATH))

    assert "innerHTML" not in render_chips
    assert "textContent" in render_chips or "createTextNode" in render_chips
