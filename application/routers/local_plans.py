import logging
from typing import Optional

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse

from application.core.templates import templates
from application.core.utils import DigitalLandJSONResponse, to_snake
from application.data_access.digital_land_queries import (
    filter_datasets,
    get_dataset_filter_fields,
)
from application.db.session import get_session
from application.search.enum import SuffixDataset
from application.search.filters import DatasetQueryFilters

router = APIRouter()
logger = logging.getLogger(__name__)


def list_local_plans(
    request: Request,
    extension: Optional[SuffixDataset] = None,
    session: Session = Depends(get_session),
    query_filters: DatasetQueryFilters = Depends(),
):
    filters = {"collection": "local-plan"}
    datasets = filter_datasets(session, **filters)

    if query_filters.dataset:
        datasets = [ds for ds in datasets if ds.dataset in query_filters.dataset]

    data = {"datasets": datasets, "feedback_form_footer": True}

    if extension is not None and extension.value == "json":
        if query_filters.field:
            include_fields = {
                to_snake(part.strip())
                for item in query_filters.field
                for part in item.split(",")
                if part.strip()
            }
            datasets = [
                get_dataset_filter_fields(ds, include_fields) for ds in datasets
            ]
            data["datasets"] = datasets

        if query_filters.exclude_field:
            exclude_fields = {
                to_snake(part.strip())
                for item in query_filters.exclude_field
                for part in item.split(",")
                if part.strip()
            }
            data["datasets"] = [
                (
                    {k: v for k, v in ds.items() if k not in exclude_fields}
                    if isinstance(ds, dict)
                    else ds.model_dump(exclude=exclude_fields, by_alias=True)
                )
                for ds in data["datasets"]
            ]
        return data
    else:
        dataset_list_url = [
            f"dataset={dataset.dataset}" for dataset in data["datasets"]
        ]
        view_as_list_query = "&".join(dataset_list_url)

        return templates.TemplateResponse(
            request,
            "local_plans.html",
            {
                "view_as_list_query": view_as_list_query,
                **data,
            },
        )


router.add_api_route(
    ".{extension}",
    endpoint=list_local_plans,
    response_class=DigitalLandJSONResponse,
    tags=["List local plans"],
    summary="This endpoint lists all datasets, returning the results in the file format specified.",
)

router.add_api_route(
    "/", endpoint=list_local_plans, response_class=HTMLResponse, include_in_schema=False
)
