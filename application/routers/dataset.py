import logging
from typing import Optional
from urllib.parse import urljoin

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse

from application.data_access.digital_land_queries import (
    get_dataset_query,
    get_datasets,
    get_latest_resource,
    get_publisher_coverage,
)
from application.data_access.entity_queries import get_entity_count, get_entity_search
from application.core.templates import templates
from application.core.utils import DigitalLandJSONResponse
from application.search.enum import SuffixDataset, SuffixLinkableFiles
from application.search.filters import DatasetQueryFilters
from application.settings import get_settings, Settings

router = APIRouter()
logger = logging.getLogger(__name__)


def list_datasets(request: Request, extension: Optional[SuffixDataset] = None):
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
        return data
    else:
        return templates.TemplateResponse(
            "dataset_index.html", {"request": request, **data}
        )


def get_dataset(
    request: Request,
    dataset: str,
    limit: int = 50,
    settings: Settings = Depends(get_settings),
    extension: Optional[SuffixDataset] = None,
):
    collection_bucket = settings.S3_COLLECTION_BUCKET
    hoisted_bucket = settings.S3_HOISTED_BUCKET
    try:
        _dataset = get_dataset_query(dataset)
        if _dataset is None:
            raise HTTPException(status_code=404, detail="dataset not found")

        entity_count = get_entity_count(dataset)

        if extension is not None and extension.value == "json":
            _dataset.entity_count = entity_count
            return _dataset

        latest_resource = get_latest_resource(dataset)
        publisher_coverage = get_publisher_coverage(dataset)

        # for categoric datasets provide list of categories
        if _dataset.typology == "category":
            entity_query_params = {"dataset": [dataset]}
            categories = get_entity_search(entity_query_params)["entities"]
            categories = [
                category.dict(by_alias=True, exclude={"geojson"})
                for category in categories
            ]
        else:
            categories = None

        return templates.TemplateResponse(
            "dataset.html",
            {
                "request": request,
                "dataset": _dataset,
                "collection_bucket": collection_bucket,
                "hoisted_bucket": hoisted_bucket,
                "entity_count": entity_count[1] if entity_count else 0,
                "publishers": {
                    "expected": publisher_coverage.expected_publisher_count,
                    "current": publisher_coverage.publisher_count,
                },
                "latest_resource": latest_resource,
                "last_collection_attempt": latest_resource.last_collection_attempt
                if latest_resource
                else None,
                "categories": categories,
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


def link_dataset(
    request: Request,
    extension: SuffixLinkableFiles,
    dataset: DatasetQueryFilters = Depends(),
    settings: Settings = Depends(get_settings),
):
    hoisted_collection_bucket = settings.S3_HOISTED_BUCKET
    return RedirectResponse(
        urljoin(hoisted_collection_bucket, f"{dataset.dataset}-hoisted.csv"),
        status_code=302,
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

router.add_api_route(
    "/{dataset}.{extension}/link",
    endpoint=link_dataset,
    response_class=RedirectResponse,
    tags=["Link dataset"],
)
