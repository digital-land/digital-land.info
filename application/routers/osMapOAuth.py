import logging
from urllib.parse import urlparse

from fastapi import APIRouter, Request, HTTPException

from application.core.filters import get_os_oauth2_token
from application.core.utils import DigitalLandJSONResponse

logger = logging.getLogger(__name__)

router = APIRouter()


def _is_same_origin(request: Request) -> bool:
    """Only the first-party map page should be able to mint an OS token.

    Browsers set Sec-Fetch-Site on the request and page JavaScript cannot
    override it, so a value of "same-origin" is a trustworthy signal that the
    call came from our own page. For browsers that do not send Sec-Fetch-Site,
    fall back to matching the Origin/Referer host against the request host.

    This is not an authentication boundary (the token is handed to the browser
    by design); it stops the endpoint being used cross-site or as an open
    token-minting oracle. Bulk-minting abuse is handled at the edge (rate
    limiting), not here.
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


def getOSMapOAuth(request: Request):
    if not _is_same_origin(request):
        raise HTTPException(status_code=403, detail="Forbidden")
    token = get_os_oauth2_token()
    return token


router.add_api_route(
    "/getToken",
    endpoint=getOSMapOAuth,
    response_class=DigitalLandJSONResponse,
)
