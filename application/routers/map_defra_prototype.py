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

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_class=HTMLResponse)
def get_defra_map_prototype(
    request: Request,
    session: Session = Depends(get_session),
    redis: Redis = Depends(get_redis),
):
    """
    Spike: same dataset/layer list as the live /map/ page, rendered
    with the Defra `@defra/interactive-map` component instead of the
    hand-rolled MapController, to compare overlay/basemap behaviour.
    """
    settings = get_settings()
    geography_datasets = get_datasets_with_data_by_geography(
        DbSession(session=session, redis=redis)
    )
    geography_datasets_dicts = [json.loads(d.json()) for d in geography_datasets]

    return templates.TemplateResponse(
        request,
        "defra-map-prototype.html",
        {
            "request": request,
            "layers": geography_datasets_dicts,
            "settings": settings,
        },
    )
