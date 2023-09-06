from application.core.filters import get_os_oauth2_token
from application.core.utils import DigitalLandJSONResponse
from fastapi import APIRouter, Request

router = APIRouter()


def getOSMapOAuth(request: Request):
    token = get_os_oauth2_token()
    return token


router.add_api_route(
    "/getToken",
    endpoint=getOSMapOAuth,
    response_class=DigitalLandJSONResponse,
)
