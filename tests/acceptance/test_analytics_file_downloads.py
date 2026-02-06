import pytest
from playwright.sync_api import Page


def test_file_download_tracking_respects_cookie_consent(
    server_url, page: Page, app_test_data
):
    """
    Tests that file download tracking is only executed when analytics cookies are accepted.

    * Mock gtag and capture calls
    * Go to a dataset page
    * Reject analytics cookies → click download → verify NO tracking
    * Accept analytics cookies → click download → verify tracking fires
    """

    # Track gtag calls in a list
    gtag_calls = []

    def capture_gtag_calls(msg):
        text = msg.text
        if "GTAG_CALLED:" in text:
            # Extract the JSON payload after "GTAG_CALLED:"
            try:
                import json

                payload = text.split("GTAG_CALLED:", 1)[1].strip()
                gtag_calls.append(json.loads(payload))
            except Exception:
                pass

    page.on("console", capture_gtag_calls)

    # Inject a mock gtag that logs to console (so we can capture it)
    page.add_init_script(
        """
        window.gtag = function(...args) {
            console.log('GTAG_CALLED:', JSON.stringify(args));
        };
    """
    )

    # Go to a dataset page
    page.goto(f"{server_url}/dataset/ancient-woodland")
    page.wait_for_load_state("networkidle")

    # REJECT analytics (additional) cookies
    page.evaluate("window.cookiePrefs = { usage: false }")

    # Find and click the first .geojson download link
    geojson_link = page.locator('a[href*=".geojson"]').first
    if geojson_link.count() > 0:
        gtag_calls.clear()  # Clear any existing calls
        # Prevent actual navigation/download so the page stays intact
        page.evaluate(
            """
            const link = document.querySelector('a[href*=".geojson"]');
            link.addEventListener('click', (e) => e.preventDefault());
            link.click();
            """
        )
        page.wait_for_timeout(500)  # Give handler time to fire

        # Should NOT see any file_download events
        file_download_events = [
            call
            for call in gtag_calls
            if len(call) >= 2 and call[0] == "event" and call[1] == "file_download"
        ]
        assert (
            len(file_download_events) == 0
        ), f"Expected no tracking when cookies rejected, but got: {file_download_events}"

    # ACCEPT analytics (additional) cookies
    page.evaluate("window.cookiePrefs = { usage: true }")

    # Click another download link
    download_link = page.locator('a[href*=".json"]').first
    if download_link.count() == 0:
        download_link = page.locator('a[href*=".geojson"]').first

    if download_link.count() > 0:
        gtag_calls.clear()
        # Prevent actual navigation/download so the page stays intact
        page.evaluate(
            """
            const link = document.querySelector('a[href*=".geojson"]');
            link.addEventListener('click', (e) => e.preventDefault());
            link.click();
            """
        )
        page.wait_for_timeout(500)

        # Should see exactly one file_download event
        file_download_events = [
            call
            for call in gtag_calls
            if len(call) >= 2 and call[0] == "event" and call[1] == "file_download"
        ]
        assert (
            len(file_download_events) == 1
        ), f"Expected 1 tracking event when cookies accepted, but got {len(file_download_events)}: {gtag_calls}"

        # Verify the event payload structure
        event_data = file_download_events[0][2]
        assert "link_url" in event_data
        assert "link_text" in event_data
        assert "file_extension" in event_data
        assert event_data["file_extension"] in [
            "geojson",
            "json",
            "xml",
            "gml",
            "kml",
            "gpkg",
            "shp",
        ]


def test_file_download_tracking_ignores_non_download_links(server_url, page: Page):
    """
    Tests that regular navigation links (non-downloads) are NOT tracked.

    * Mock gtag and capture calls
    * Go to homepage
    * Accept analytics cookies → click regular link(s) → verify NO tracking
    """

    gtag_calls = []

    def capture_gtag_calls(msg):
        text = msg.text
        if "GTAG_CALLED:" in text:
            try:
                import json

                payload = text.split("GTAG_CALLED:", 1)[1].strip()
                gtag_calls.append(json.loads(payload))
            except Exception:
                pass

    page.on("console", capture_gtag_calls)

    page.add_init_script(
        """
        window.gtag = function(...args) {
            console.log('GTAG_CALLED:', JSON.stringify(args));
        };
    """
    )

    # Go to homepage
    page.goto(f"{server_url}/")
    page.wait_for_load_state("networkidle")

    # Accept analytics cookies
    page.evaluate("window.cookiePrefs = { usage: true }")

    # Inject a test link that's NOT a download
    page.evaluate(
        """
        const link = document.createElement('a');
        link.href = '/some-page';
        link.innerText = 'Regular Link';
        link.id = 'test-regular-link';
        document.body.appendChild(link);
    """
    )

    # Click the injected regular link and prevent navigation
    gtag_calls.clear()
    page.evaluate(
        """
        const link = document.getElementById('test-regular-link');
        link.addEventListener('click', (e) => e.preventDefault());
        link.click();
    """
    )
    page.wait_for_timeout(500)

    # Should NOT see any file_download events
    file_download_events = [
        call
        for call in gtag_calls
        if len(call) >= 2 and call[0] == "event" and call[1] == "file_download"
    ]
    assert (
        len(file_download_events) == 0
    ), f"Regular links should not trigger file_download tracking, but got: {file_download_events}"


@pytest.mark.parametrize(
    "extension", ["geojson", "json", "xml", "gml", "kml", "gpkg", "shp"]
)
def test_file_download_tracking_captures_different_extensions(
    server_url, page: Page, extension
):
    """
    Tests that all tracked file extensions are properly captured.

    Uses mock links since not all extensions may exist on dataset pages.
    """

    gtag_calls = []

    def capture_gtag_calls(msg):
        text = msg.text
        if "GTAG_CALLED:" in text:
            try:
                import json

                payload = text.split("GTAG_CALLED:", 1)[1].strip()
                gtag_calls.append(json.loads(payload))
            except Exception:
                pass

    page.on("console", capture_gtag_calls)

    page.add_init_script(
        """
        window.gtag = function(...args) {
            console.log('GTAG_CALLED:', JSON.stringify(args));
        };
    """
    )

    page.goto(f"{server_url}/")
    page.wait_for_load_state("networkidle")

    # Accept analytics cookies
    page.evaluate("window.cookiePrefs = { usage: true }")

    # Inject a test link with the desired extension
    page.evaluate(
        f"""
        const link = document.createElement('a');
        link.href = 'https://example.com/test.{extension}';
        link.innerText = 'Test {extension.upper()} Download';
        link.id = 'test-download-link';
        document.body.appendChild(link);
    """
    )

    # Click the injected link
    gtag_calls.clear()
    page.evaluate(
        """
        const link = document.getElementById('test-download-link');
        link.addEventListener('click', (e) => e.preventDefault());
        link.click();
        """
    )
    page.wait_for_timeout(500)

    # Should see one file_download event
    file_download_events = [
        call
        for call in gtag_calls
        if len(call) >= 2 and call[0] == "event" and call[1] == "file_download"
    ]
    assert len(file_download_events) == 1

    # Verify the extension is captured correctly
    event_data = file_download_events[0][2]
    assert event_data["file_extension"] == extension
    assert event_data["link_url"] == f"https://example.com/test.{extension}"
