import logging
from typing import Optional

from application.search.filters import DatasetQueryFilters
from fastapi import APIRouter, Request, HTTPException, Path, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from redis import Redis

from application.data_access.digital_land_queries import (
    get_dataset_filter_fields,
    get_dataset_query,
    get_all_datasets,
    get_latest_resource,
    get_publisher_coverage,
)

from pydantic import Required
from application.data_access.entity_queries import get_entity_count, get_entity_search
from application.core.templates import templates
from application.core.utils import DigitalLandJSONResponse, to_snake
from application.search.enum import SuffixDataset
from application.settings import get_settings, Settings
from application.db.session import get_session, get_redis, DbSession


router = APIRouter()
logger = logging.getLogger(__name__)


def get_origin_label(dataset):
    labels = {
        "alpha": (
            "Data created by MHCLG. We will replace this with data from authoritative sources "
            "when it is available."
        ),
        "beta": (
            "Contains some data created by MHCLG. We are working to replace it with data "
            "from authoritative sources"
        ),
        "live": "All data from authoritative sources",
        "live+": "All data from authoritative sources with additional supporting data.",
    }
    return labels.get(dataset.phase, "Unknown")


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
    query_filters: DatasetQueryFilters = Depends(),
    session: Session = Depends(get_session),
    redis: Redis = Depends(get_redis),
):
    datasets = get_all_datasets(DbSession(session=session, redis=redis))

    if query_filters.dataset:
        datasets = [ds for ds in datasets if ds.dataset in query_filters.dataset]

    entity_counts_response = get_entity_count(session)
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
        if query_filters.field:
            datasets = [
                get_dataset_filter_fields(ds, query_filters.field) for ds in datasets
            ]
            data["datasets"] = datasets

        if query_filters.exclude_field:
            exclude_fields = set(
                to_snake(field.strip())
                for field in query_filters.exclude_field.split(",")
            )
            data["datasets"] = [
                ds
                if isinstance(ds, dict)
                else ds.dict(exclude=exclude_fields, by_alias=True)
                for ds in data["datasets"]
            ]

        if not query_filters.include_typologies:
            data["typologies"] = ""
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
    session: Session = Depends(get_session),
):
    data_file_url = settings.DATA_FILE_URL
    try:
        _dataset = get_dataset_query(session, dataset)
        if _dataset is None:
            raise HTTPException(status_code=404, detail="dataset not found")

        entity_count = get_entity_count(session, dataset)

        if extension is not None and extension.value == "json":
            _dataset.entity_count = entity_count
            return _dataset

        latest_resource = get_latest_resource(session, dataset)
        publisher_coverage = get_publisher_coverage(session, dataset)
        # TODO add test to check this table loads loads
        # for categoric datasets provide list of categories
        if _dataset.typology == "category":
            entity_query_params = {"dataset": [dataset]}
            categories = get_entity_search(session, entity_query_params)["entities"]
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
                "last_collection_attempt": (
                    latest_resource.last_collection_attempt if latest_resource else None
                ),
                "categories": categories,
                "data_file_url": data_file_url,
                "dataset_origin_label": get_origin_label(_dataset),
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
    summary="This endpoint lists all datasets, returning the results in the file format specified.",
)

router.add_api_route(
    "/", endpoint=list_datasets, response_class=HTMLResponse, include_in_schema=False
)

router.add_api_route(
    "/{dataset}.{extension}",
    endpoint=get_dataset,
    response_class=DigitalLandJSONResponse,
    tags=["Get dataset"],
    summary="This endpoint returns a specific dataset in the file format specified.",
)
router.add_api_route(
    "/{dataset}",
    endpoint=get_dataset,
    response_class=HTMLResponse,
    include_in_schema=False,
)
