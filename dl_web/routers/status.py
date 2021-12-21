import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from dl_web.search.enum import Suffix


router = APIRouter()
logger = logging.getLogger(__name__)


async def get_status_page(
    request: Request, status: int, extension: Optional[Suffix] = None
):
    if status == 410:
        raise HTTPException(status_code=410, detail="Gone")

    if status == 500:
        raise HTTPException(status_code=500, detail="Internal Server Error")

    raise HTTPException(status_code=404, detail="Item not found")


router.add_api_route(
    "/{status}",
    endpoint=get_status_page,
    response_class=HTMLResponse,
    include_in_schema=False,
)
