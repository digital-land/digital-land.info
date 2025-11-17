import logging

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from redis import Redis
from application.settings import get_settings
from application.core.templates import templates
from application.data_access.digital_land_queries import (
    get_datasets_with_data_by_geography,
)
from application.db.session import get_session, get_redis, DbSession
from application.data_access.find_an_area_helpers import find_an_area

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_class=HTMLResponse)
def get_map(
    request: Request,
    session: Session = Depends(get_session),
    redis: Redis = Depends(get_redis),
):
    settings = get_settings()
    geography_datasets = get_datasets_with_data_by_geography(
        DbSession(session=session, redis=redis)
    )

    # Extract the 'q' query parameter from the request
    search_query = request.query_params.get("q", "").strip()
    search_result = find_an_area(search_query) if search_query else None

    return templates.TemplateResponse(
        "national-map.html",
        {
            "request": request,
            "layers": geography_datasets,
            "settings": settings,
            "search_query": search_query,
            "search_result": search_result,
            "feedback_form_footer": True,
        },
    )
