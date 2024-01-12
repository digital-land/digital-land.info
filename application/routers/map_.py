import logging

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from application.settings import get_settings
from application.core.templates import templates
from application.data_access.digital_land_queries import (
    get_datasets_with_data_by_typology,
)
from application.db.session import get_session

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_class=HTMLResponse)
def get_map(request: Request, session: Session = Depends(get_session)):
    settings = get_settings()
    geography_datasets = get_datasets_with_data_by_typology(session, "geography")
    return templates.TemplateResponse(
        "national-map.html",
        {"request": request, "layers": geography_datasets, "settings": settings},
    )
