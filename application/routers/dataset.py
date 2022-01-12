import logging
from typing import Optional

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from starlette.responses import JSONResponse

from application.data_access.digital_land_queries import (
    get_dataset_query,
    fetch_publisher_coverage_count,
    fetch_latest_resource,
    fetch_lastest_log_date,
    get_datasets,
)
from application.data_access.entity_queries import get_entity_count
from application.core.templates import templates
from application.core.utils import DigitalLandJSONResponse
from application.search.enum import Suffix
from application.settings import get_settings, Settings

router = APIRouter()
logger = logging.getLogger(__name__)


def list_datasets(request: Request, extension: Optional[Suffix] = None):
    datasets = get_datasets()
    entity_counts_response = get_entity_count()
    entity_counts = {count[0]: count[1] for count in entity_counts_response}
    # add entity count if available
    for dataset in datasets:
        count = (
            entity_counts.get(dataset.dataset)
            if entity_counts.get(dataset.dataset)
            else 0
        )
        dataset.entity_count = count

    themes = {}

    for ds in (d for d in datasets if d.themes):
        for theme in ds.themes:
            themes.setdefault(theme, {"dataset": []})
            if ds.entity_count > 0:
                themes[theme]["dataset"].append(ds)

    data = {"datasets": datasets, "themes": themes}
    if extension is not None and extension.value == "json":
        return JSONResponse(data)
    else:
        return templates.TemplateResponse(
            "dataset_index.html", {"request": request, **data}
        )


def get_dataset(
    request: Request,
    dataset: str,
    limit: int = 50,
    settings: Settings = Depends(get_settings),
):
    collection_bucket = settings.S3_COLLECTION_BUCKET
    try:
        _dataset = get_dataset_query(dataset)
        entity_count = get_entity_count(dataset)
        publisher_coverage_response = fetch_publisher_coverage_count(dataset)
        latest_resource_response = fetch_latest_resource(dataset)
        latest_log_response = fetch_lastest_log_date(dataset)
        latest_resource = None
        if len(latest_resource_response["rows"]):
            latest_resource = {
                "resource": latest_resource_response["rows"][0][0],
                "collected_date": latest_resource_response["rows"][0][3],
            }

        return templates.TemplateResponse(
            "dataset.html",
            {
                "request": request,
                "dataset": _dataset,
                "collection_bucket": collection_bucket,
                "entity_count": entity_count[1] if entity_count else 0,
                "publishers": {
                    "expected": publisher_coverage_response["rows"][0][0],
                    "current": publisher_coverage_response["rows"][0][1],
                },
                "latest_resource": latest_resource,
                "last_collection_attempt": latest_log_response["rows"][0][1]
                if len(latest_log_response["rows"])
                else None,
            },
        )
    except KeyError as e:
        logger.exception(e)
        return templates.TemplateResponse(
            "dataset-backlog.html",
            {
                "request": request,
                "name": dataset.replace("-", " ").capitalize(),
            },
        )


router.add_api_route(
    ".{extension}",
    endpoint=list_datasets,
    response_class=DigitalLandJSONResponse,
    tags=["List datasets"],
)
router.add_api_route(
    "/", endpoint=list_datasets, response_class=HTMLResponse, include_in_schema=False
)

router.add_api_route(
    "/{dataset}.{extension}",
    endpoint=get_dataset,
    response_class=DigitalLandJSONResponse,
    tags=["Get dataset"],
)
router.add_api_route(
    "/{dataset}",
    endpoint=get_dataset,
    response_class=HTMLResponse,
    include_in_schema=False,
)
