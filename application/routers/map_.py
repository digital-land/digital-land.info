import logging

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from application.core.templates import templates
from application.data_access.digital_land_queries import (
    get_datasets_with_data_by_typology,
)


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_class=HTMLResponse)
def get_map(request: Request):
    geography_datasets = get_datasets_with_data_by_typology("geography")
    return templates.TemplateResponse(
        "national-map.html", {"request": request, "layers": geography_datasets}
    )
