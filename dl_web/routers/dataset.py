import logging
from typing import Optional

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from starlette.responses import JSONResponse

from dl_web.core.models import Dataset
from dl_web.data_access.digital_land_queries import get_dataset, get_datasets_with_theme
from dl_web.data_access.entity_queries import EntityQuery
from dl_web.core.resources import specification, templates
from dl_web.core.utils import create_dict
from dl_web.search.enum import Suffix
from dl_web.settings import get_settings, Settings

router = APIRouter()
logger = logging.getLogger(__name__)


async def get_index(request: Request, extension: Optional[Suffix] = None):
    response = await get_datasets_with_theme()
    results = [create_dict(response["columns"], row) for row in response["rows"]]
    datasets = [d for d in results if d["dataset_active"]]
    themes = {}
    for d in datasets:
        dataset_themes = d["dataset_themes"].split(";")
        for theme in dataset_themes:
            themes.setdefault(theme, {"dataset": []})
            themes[theme]["dataset"].append(d)

    data = {"datasets": datasets, "themes": themes}
    if extension is not None and extension.value == "json":
        return JSONResponse(data)
    else:
        return templates.TemplateResponse(
            "dataset_index.html", {"request": request, **data}
        )


async def get_dataset_index(
    request: Request,
    dataset: str,
    limit: int = 50,
    extension: Optional[Suffix] = None,
    settings: Settings = Depends(get_settings),
):
    collection_bucket = settings.S3_COLLECTION_BUCKET
    try:
        _dataset = await get_dataset(dataset)
        typology = specification.field_typology(dataset)
        params = {
            "typology": [_dataset.typology],
            "dataset": [dataset],
            "limit": limit,
        }
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
                    "key_field": specification.key_field(typology),
                    "collection_bucket": collection_bucket,
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
    endpoint=get_index,
    response_class=JSONResponse,
    response_model=Dataset,
)
router.add_api_route(
    "/", endpoint=get_index, response_class=HTMLResponse, include_in_schema=False
)

router.add_api_route(
    "/{dataset}.{extension}",
    endpoint=get_dataset_index,
    response_class=JSONResponse,
    response_model=Dataset,
)
router.add_api_route(
    "/{dataset}",
    endpoint=get_dataset_index,
    response_class=HTMLResponse,
    include_in_schema=False,
)
