import logging
from typing import Optional

from fastapi import APIRouter, Request, HTTPException, Path, Depends
from fastapi.responses import HTMLResponse

from application.data_access.digital_land_queries import (
    get_dataset_query,
    get_datasets,
    get_latest_resource,
    get_publisher_coverage,
)

from pydantic import Required
from application.data_access.entity_queries import get_entity_count, get_entity_search
from application.core.templates import templates
from application.core.utils import DigitalLandJSONResponse
from application.search.enum import SuffixDataset
from application.settings import get_settings, Settings


router = APIRouter()
logger = logging.getLogger(__name__)


def get_datasets_by_typology(datasets):
    typologies = {}
    for ds in (d for d in datasets if d.typology):
        typology = ds.typology
        typologies.setdefault(typology, {"dataset": []})
        if ds.entity_count > 0:
            typologies[typology]["dataset"].append(ds)

    return typologies


def list_datasets(
    request: Request,
    extension: Optional[SuffixDataset] = None,
):
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

    typologies = get_datasets_by_typology(datasets)

    data = {"datasets": datasets, "typologies": typologies}
    if extension is not None and extension.value == "json":
        return data
    else:
        return templates.TemplateResponse(
            "dataset_index.html", {"request": request, **data}
        )


def get_dataset(
    request: Request,
    dataset: str = Path(default=Required, description="Specify which dataset"),
    settings: Settings = Depends(get_settings),
    # limit: int = Path(default=50,description="Limit number of rows in the response"),
    extension: Optional[SuffixDataset] = None,
):
    data_file_url = settings.DATA_FILE_URL
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
                "data_file_url": data_file_url,
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
