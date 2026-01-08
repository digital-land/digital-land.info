import json
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

    # Convert DatasetModel objects to dictionaries so that it can be used in
    # the template
    geography_datasets_dicts = [json.loads(d.json()) for d in geography_datasets]

    # Extract the 'q' query parameter from the request
    search_query = request.query_params.get("q", "").strip()

    search_result = find_an_area(search_query) if search_query else None

    # Get paint options when search type is "lpa"
    entity_paint_options = None
    if search_result and search_result.get("type") == "lpa":
        result = search_result.get("result")
        if result and result.get("dataset"):
            dataset = result.get("dataset")
            matching_datasets = [d for d in geography_datasets if d.dataset == dataset]
            if matching_datasets:
                entity_paint_options = matching_datasets[0].paint_options

    return templates.TemplateResponse(
        "national-map.html",
        {
            "request": request,
            "layers": geography_datasets_dicts,
            "settings": settings,
            "search_query": search_query,
            "search_result": search_result,
            "entity_paint_options": entity_paint_options,
            "feedback_form_footer": True,
        },
    )
