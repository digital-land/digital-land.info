import logging
import re
import threading
import time
from urllib.parse import quote, urlparse

import requests
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import JSONResponse

from application.core.filters import get_os_oauth2_token

logger = logging.getLogger(__name__)

router = APIRouter()

OS_MAPS_BASE_URL = "https://api.os.uk/maps/"
CACHE_CONTROL = "public, max-age=86400"
TOKEN_EXPIRY_BUFFER_SECONDS = 30

_token_cache = {"access_token": None, "expires_at": 0}
_token_lock = threading.Lock()

# The only OS Vector Tile API resources the map needs. Paths are matched
# against the already-decoded path in full, and no pattern allows "." or "/"
# inside a segment, so dot-segments (raw or percent-encoded) can never reach
# upstream and the credential can't be pointed at other OS products.
ALLOWED_PATHS = [
    re.compile(r"vector/v1/vts"),
    re.compile(r"vector/v1/vts/tile/\d{1,2}/\d{1,7}/\d{1,7}\.pbf"),
    re.compile(r"vector/v1/vts/resources/sprites/sprite(@2x)?\.(json|png)"),
    re.compile(
        r"vector/v1/vts/resources/fonts/[A-Za-z0-9 ,-]{1,200}/\d{1,5}-\d{1,5}\.pbf"
    ),
]

# Query parameters are fixed server-side; anything the client sends is dropped.
UPSTREAM_PARAMS = {"srs": "3857", "key": "null"}


def _is_allowed_path(path: str) -> bool:
    return any(pattern.fullmatch(path) for pattern in ALLOWED_PATHS)


def _is_same_origin(request: Request) -> bool:
    """
    Only our own map pages should be able to drive this proxy.

    Browsers set Sec-Fetch-Site on the request and page JavaScript cannot
    override it, so a value of "same-origin" is a trustworthy signal that the
    call came from our own page. For browsers that do not send Sec-Fetch-Site,
    fall back to matching the Origin/Referer host against the request host.
    """
    sec_fetch_site = request.headers.get("sec-fetch-site")
    if sec_fetch_site is not None:
        return sec_fetch_site == "same-origin"

    host = request.headers.get("host")
    for header in ("origin", "referer"):
        value = request.headers.get(header)
        if value:
            return bool(host) and urlparse(value).netloc == host
    return False


def _get_cached_os_token() -> str:
    """
    Returns a cached OS OAuth2 bearer token, minting a new one only once
    the cached token is close to expiry.
    """
    with _token_lock:
        if time.time() < _token_cache["expires_at"] - TOKEN_EXPIRY_BUFFER_SECONDS:
            return _token_cache["access_token"]

        token = get_os_oauth2_token()
        if not isinstance(token, dict) or "access_token" not in token:
            raise ConnectionError(f"Failed to obtain OS OAuth2 token: {token}")

        try:
            expires_in = int(token["expires_in"])
        except (KeyError, TypeError, ValueError):
            raise ConnectionError(
                "OS OAuth2 token response has invalid expires_in: "
                f"{token.get('expires_in')!r}"
            )

        _token_cache["access_token"] = token["access_token"]
        _token_cache["expires_at"] = time.time() + expires_in
        return _token_cache["access_token"]


def _rewrite_os_urls(value, proxy_base_url: str):
    """
    Rewrite any embedded api.os.uk URLs (e.g. in the VTS TileJSON metadata
    document) so follow-up requests MapLibre makes go through this proxy too.

    These must be absolute, not relative: MapLibre fetches actual tiles from
    inside a Web Worker, whose base URL is a blob: URL, so a relative path
    can't be resolved to a fetchable request there.
    """
    if isinstance(value, str):
        if value.startswith(OS_MAPS_BASE_URL):
            return proxy_base_url + value[len(OS_MAPS_BASE_URL) :]
        return value
    if isinstance(value, list):
        return [_rewrite_os_urls(item, proxy_base_url) for item in value]
    if isinstance(value, dict):
        return {
            key: _rewrite_os_urls(item, proxy_base_url) for key, item in value.items()
        }
    return value


def get_os_map_resource(request: Request, path: str):
    """
    Proxies OS vector tile/sprite/glyph requests server-side, so the OS
    OAuth2 bearer token never reaches the browser.
    """
    if not _is_same_origin(request):
        raise HTTPException(status_code=403, detail="Forbidden")

    if not _is_allowed_path(path):
        raise HTTPException(status_code=404, detail="Not Found")

    try:
        token = _get_cached_os_token()
    except ConnectionError as e:
        logger.error(f"Could not obtain OS OAuth2 token: {e}")
        raise HTTPException(status_code=502, detail="Upstream authentication failed")

    try:
        upstream = requests.get(
            OS_MAPS_BASE_URL + quote(path, safe="/,@"),
            params=UPSTREAM_PARAMS,
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
    except requests.RequestException as e:
        logger.error(f"OS maps proxy request failed: {e}")
        raise HTTPException(status_code=502, detail="Upstream request failed")

    content_type = upstream.headers.get("content-type", "application/octet-stream")

    if not upstream.ok:
        return Response(
            content=upstream.content,
            media_type=content_type,
            status_code=upstream.status_code,
        )

    if "json" in content_type:
        try:
            parsed = upstream.json()
        except ValueError as e:
            logger.error(f"OS maps proxy returned invalid JSON: {e}")
            raise HTTPException(
                status_code=502, detail="Upstream returned invalid response"
            )

        proxy_base_url = f"{request.url.scheme}://{request.url.netloc}/os/maps/"
        return JSONResponse(
            content=_rewrite_os_urls(parsed, proxy_base_url),
            headers={"Cache-Control": CACHE_CONTROL},
        )

    return Response(
        content=upstream.content,
        media_type=content_type,
        headers={"Cache-Control": CACHE_CONTROL},
    )


router.add_api_route(
    "/maps/{path:path}",
    endpoint=get_os_map_resource,
    include_in_schema=False,
)
