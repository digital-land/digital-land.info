import json
import logging

from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from redis import Redis
from application.settings import get_settings
from application.core.templates import templates
from application.data_access.digital_land_queries import (
    get_datasets_with_data_by_geography,
    get_dataset_quality_values,
)
from application.core.utils import ENTITY_QUALITY_DESCRIPTION
from application.db.session import get_session, get_redis, DbSession
from application.data_access.find_an_area_helpers import find_an_area
from application.data_access.os_api import is_valid_postcode


router = APIRouter()
logger = logging.getLogger(__name__)


def get_quality_colour(quality: str) -> str:
    """
    Map quality values to colours for visualization.
    """
    quality_colours = {
        "authoritative": "#CCE2D8",
        "some": "#FFF7BF",
        "usable": "#817D0D",
        "trustworthy": "#3ffd00",
    }
    return quality_colours.get(
        quality, "#FCD6C3"
    )  # Default orange if no quality data is found


@router.get("/", response_class=HTMLResponse)
def get_map(
    request: Request,
    session: Session = Depends(get_session),
    redis: Redis = Depends(get_redis),
    # Handle query params
    search_query: str = Query(None, alias="q"),
    search_type: str = Query(None, alias="type"),
):
    # Determines if a form was actually submitted (to trigger validation).
    #
    # If `search_query` is truthy we avoid checking `request.query_params`
    # which in tests may be a Mock that raises on membership checks.
    #
    # If the membership check raises, fall back to the presence of
    # `search_query`.
    query_params = getattr(request, "query_params", None)
    try:
        form_submitted = bool(search_query) or ("q" in query_params)
    except Exception:
        form_submitted = bool(search_query)

    settings = get_settings()
    geography_datasets = get_datasets_with_data_by_geography(
        DbSession(session=session, redis=redis)
    )

    # Convert DatasetModel objects to dictionaries so that it can be used
    # in the template
    geography_datasets_dicts = [json.loads(d.json()) for d in geography_datasets]

    # Get quality information for all datasets
    dataset_names = [dataset.dataset for dataset in geography_datasets]
    dataset_quality_map = get_dataset_quality_values(session, dataset_names)

    # Generate data quality layers
    data_quality_info = []
    for dataset in geography_datasets:
        dataset_name = dataset.dataset
        quality_values = dataset_quality_map.get(dataset_name, [])

        for quality in quality_values:
            description = ENTITY_QUALITY_DESCRIPTION.get(quality, "We have no data")
            if description:
                quality_layer = {
                    "dataset": f"{dataset_name}-{quality}",
                    "name": f"{dataset.name} - {description}",
                    "description": description,
                    "quality": quality,
                    "source_dataset": dataset_name,
                    "paint_options": {
                        "colour": get_quality_colour(quality),
                        "opacity": 0.7,
                    },
                }
                data_quality_info.append(quality_layer)

    search_result = None
    error = ""
    entity_paint_options = None

    if form_submitted:
        search_query = search_query.strip() if search_query else ""

        # Validation logic
        if search_query == "":
            if search_type == "postcode":
                error = "Enter a postcode"
            elif search_type == "uprn":
                error = "Enter a UPRN"
            elif search_type == "lpa":
                error = "Select a local planning authority"
        else:
            if search_type == "postcode":
                if not is_valid_postcode(search_query):
                    error = "Enter a full UK postcode"
            elif search_type == "uprn" and not search_query.isdigit():
                error = "UPRN must be a number"
            elif search_type == "uprn" and len(search_query) > 12:
                error = "UPRN must be up to 12 digits"

        # Execution logic
        if not error and (search_query and search_type):
            search_result = find_an_area(search_query, search_type)

            # Paint options when search type is "lpa"
            entity_paint_options = None
            if search_result and search_type == "lpa":
                result = search_result.get("result")
                if result and result.get("dataset"):
                    dataset = result.get("dataset")
                    matching_datasets = [
                        d for d in geography_datasets if d.dataset == dataset
                    ]
                    if matching_datasets:
                        entity_paint_options = matching_datasets[0].paint_options

    # Build template context and only include `error` when present so
    # unit tests that don't expect the key remain stable.
    context = {
        "request": request,
        "layers": geography_datasets_dicts,
        "data_quality_info": data_quality_info,
        "settings": settings,
        "search_query": search_query,
        "search_result": search_result,
        "entity_paint_options": entity_paint_options,
        "feedback_form_footer": True,
    }

    if error:
        context["error"] = error

    return templates.TemplateResponse("national-map.html", context)
