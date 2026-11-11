from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException

from application.routers import os_map_proxy
from application.routers.os_map_proxy import (
    _get_cached_os_token,
    _is_same_origin,
    _rewrite_os_urls,
    get_os_map_resource,
)


def req(headers):
    return SimpleNamespace(headers=headers)


def fake_request(headers=None):
    return SimpleNamespace(
        headers=headers or {"sec-fetch-site": "same-origin"},
        query_params={},
        url=SimpleNamespace(scheme="https", netloc="planning.data.gov.uk"),
    )


def reset_token_cache():
    os_map_proxy._token_cache["access_token"] = None
    os_map_proxy._token_cache["expires_at"] = 0


def test_is_same_origin_uses_sec_fetch_site_header():
    """
    Sec-Fetch-Site can't be set by page JS, so it's trusted when present.
    """
    assert _is_same_origin(req({"sec-fetch-site": "same-origin"})) is True
    assert _is_same_origin(req({"sec-fetch-site": "cross-site"})) is False
    assert _is_same_origin(req({"sec-fetch-site": "none"})) is False


def test_is_same_origin_falls_back_to_origin_referer_host_match():
    """
    Browsers that omit Sec-Fetch-Site are checked against Origin/Referer instead.
    """
    assert (
        _is_same_origin(
            req(
                {
                    "host": "planning.data.gov.uk",
                    "origin": "https://planning.data.gov.uk",
                }
            )
        )
        is True
    )
    assert (
        _is_same_origin(
            req({"host": "planning.data.gov.uk", "origin": "https://evil.example"})
        )
        is False
    )


def test_is_same_origin_rejects_when_no_origin_signal_present():
    """
    With neither Sec-Fetch-Site nor Origin/Referer, the request is rejected.
    """
    assert _is_same_origin(req({"host": "planning.data.gov.uk"})) is False


PROXY_BASE_URL = "https://planning.data.gov.uk/os/maps/"


def test_rewrite_os_urls_rewrites_matching_strings_to_an_absolute_url():
    """
    api.os.uk/maps URLs become absolute proxy URLs, not relative paths:
    MapLibre fetches tiles from a Web Worker, where a relative path can't be
    resolved to a fetchable request.
    """
    assert (
        _rewrite_os_urls(
            "https://api.os.uk/maps/vector/v1/vts/tile/1/2/3.pbf", PROXY_BASE_URL
        )
        == "https://planning.data.gov.uk/os/maps/vector/v1/vts/tile/1/2/3.pbf"
    )


def test_rewrite_os_urls_leaves_unrelated_strings_untouched():
    """
    Strings that aren't api.os.uk/maps URLs pass through unchanged.
    """
    assert (
        _rewrite_os_urls("https://example.com/not-os", PROXY_BASE_URL)
        == "https://example.com/not-os"
    )


def test_rewrite_os_urls_recurses_through_lists_and_dicts():
    """
    The TileJSON metadata document nests URLs inside lists/dicts, not just at the top level.
    """
    value = {
        "tiles": ["https://api.os.uk/maps/vector/v1/vts/tile/{z}/{x}/{y}.pbf"],
        "name": "esri",
    }
    assert _rewrite_os_urls(value, PROXY_BASE_URL) == {
        "tiles": [
            "https://planning.data.gov.uk/os/maps/vector/v1/vts/tile/{z}/{x}/{y}.pbf"
        ],
        "name": "esri",
    }


def test_get_cached_os_token_caches_a_valid_token():
    """
    A well-formed token response is cached and reused rather than re-minted
    on every call.
    """
    reset_token_cache()
    with patch.object(
        os_map_proxy,
        "get_os_oauth2_token",
        return_value={"access_token": "abc", "expires_in": 300},
    ) as mock_mint:
        assert _get_cached_os_token() == "abc"
        assert _get_cached_os_token() == "abc"
        mock_mint.assert_called_once()
    reset_token_cache()


def test_get_cached_os_token_raises_when_expires_in_missing():
    """
    A 200 response missing expires_in must be treated as a failed mint, not
    cached with an un-expirable token. The error must not echo access_token,
    since it ends up in application logs.
    """
    reset_token_cache()
    with patch.object(
        os_map_proxy,
        "get_os_oauth2_token",
        return_value={"access_token": "super-secret-token"},
    ):
        with pytest.raises(ConnectionError) as exc_info:
            _get_cached_os_token()
    assert "super-secret-token" not in str(exc_info.value)
    reset_token_cache()


def test_get_cached_os_token_raises_when_expires_in_not_numeric():
    """
    A non-numeric expires_in (e.g. null) must also be treated as a failed mint
    """
    reset_token_cache()
    with patch.object(
        os_map_proxy,
        "get_os_oauth2_token",
        return_value={"access_token": "super-secret-token", "expires_in": None},
    ):
        with pytest.raises(ConnectionError) as exc_info:
            _get_cached_os_token()
    assert "super-secret-token" not in str(exc_info.value)
    reset_token_cache()


def test_get_os_map_resource_returns_502_on_invalid_upstream_json():
    """
    A malformed JSON body from OS must degrade to the same clean 502 every
    other upstream failure in this proxy returns, not an unhandled 500.
    """
    upstream_response = Mock(ok=True, status_code=200, content=b"not json")
    upstream_response.headers = {"content-type": "application/json"}
    upstream_response.json.side_effect = ValueError("invalid json")

    with patch.object(
        os_map_proxy, "_get_cached_os_token", return_value="token"
    ), patch.object(os_map_proxy.requests, "get", return_value=upstream_response):
        with pytest.raises(HTTPException) as exc_info:
            get_os_map_resource(fake_request(), "vector/v1/vts")

    assert exc_info.value.status_code == 502
