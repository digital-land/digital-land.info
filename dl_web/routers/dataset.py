import logging
from typing import Optional

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from starlette.responses import JSONResponse

from dl_web.data_access.digital_land_queries import (
    fetch_dataset,
    fetch_datasets_with_theme,
    fetch_publisher_coverage_count,
    fetch_latest_resource,
    fetch_lastest_log_date,
)
from dl_web.data_access.entity_queries import EntityQuery, fetch_entity_count
from dl_web.core.templates import templates
from dl_web.core.utils import create_dict, DigitalLandJSONResponse
from dl_web.search.enum import Suffix
from dl_web.settings import get_settings, Settings

router = APIRouter()
logger = logging.getLogger(__name__)


async def list_datasets(request: Request, extension: Optional[Suffix] = None):
    response = await fetch_datasets_with_theme()
    entity_counts_response = await fetch_entity_count()
    entity_counts = {count[0]: count[1] for count in entity_counts_response["rows"]}
    results = [create_dict(response["columns"], row) for row in response["rows"]]
    datasets = []
    # add entity count if available
    for dataset in results:
        count = (
            entity_counts.get(dataset["dataset"])
            if entity_counts.get(dataset["dataset"])
            else 0
        )
        dataset.update({"entity_count": count})
        datasets.append(dataset)
    themes = {}

    for d in datasets:
        dataset_themes = d["dataset_themes"].split(";")
        for theme in dataset_themes:
            themes.setdefault(theme, {"dataset": []})
            if d["entity_count"] > 0:
                themes[theme]["dataset"].append(d)

    data = {"datasets": datasets, "themes": themes}
    if extension is not None and extension.value == "json":
        return JSONResponse(data)
    else:
        return templates.TemplateResponse(
            "dataset_index.html", {"request": request, **data}
        )


async def get_dataset(
    request: Request,
    dataset: str,
    limit: int = 50,
    extension: Optional[Suffix] = None,
    settings: Settings = Depends(get_settings),
):
    collection_bucket = settings.S3_COLLECTION_BUCKET
    try:
        _dataset = await fetch_dataset(dataset)
        entity_count_repsonse = await fetch_entity_count(dataset=dataset)
        publisher_coverage_response = await fetch_publisher_coverage_count(dataset)
        latest_resource_response = await fetch_latest_resource(dataset)
        latest_log_response = await fetch_lastest_log_date(dataset)
        params = {
            "typology": [_dataset.typology],
            "dataset": [dataset],
            "limit": limit,
        }
        latest_resource = None
        if len(latest_resource_response["rows"]):
            latest_resource = {
                "resource": latest_resource_response["rows"][0][0],
                "collected_date": latest_resource_response["rows"][0][3],
            }
        # TODO I don't think this page needs anything more than an entity count
        # now - and if so, note the limit param above if we try to do a count
        query = EntityQuery(params=params)
        entities = query.execute()
        if extension is not None and extension.value == "json":
            _dataset.entities = entities["results"]
            return _dataset
        else:
            return templates.TemplateResponse(
                "dataset.html",
                {
                    "request": request,
                    "dataset": _dataset,
                    "entities": entities["results"],
                    "collection_bucket": collection_bucket,
                    "entity_count": entity_count_repsonse["rows"][0][1],
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
