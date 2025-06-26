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
from application.data_access.os_api import search

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
    search_result = None

    if search_query:
        try:
            search_response = search(search_query) or []
            type = "uprn" if search_query.isdigit() else "postcode"
            result = search_response[0] if len(search_response) else None
            name = (
                (result["POSTCODE"] if type == "postcode" else result["UPRN"])
                if result
                else None
            )

            search_result = {
                "type": type,
                "query": search_query,
                "result": result,
                "geometry": {
                    "name": name,
                    "type": "point",
                    "data": {
                        "type": "Point",
                        "coordinates": [result["LNG"], result["LAT"]],
                        "properties": {
                            **result,
                            "name": name,
                        },
                    },
                }
                if result
                else None,
            }
        except Exception as e:
            logger.warning(f"Search failed for query '{search_query}': {str(e)}")
            # Continue without search result - the map will still render
            search_result = None

    return templates.TemplateResponse(
        "national-map.html",
        {
            "request": request,
            "layers": geography_datasets,
            "settings": settings,
            "search_query": search_query,
            "search_result": search_result,
        },
    )
