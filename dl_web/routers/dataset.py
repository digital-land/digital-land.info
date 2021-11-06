import logging

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from dl_web.data_access.digital_land_queries import get_dataset, get_datasets_with_theme
from dl_web.data_access.entity_queries import EntityQuery
from dl_web.resources import specification, templates
from dl_web.utils import create_dict

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    response = await get_datasets_with_theme()
    results = [create_dict(response["columns"], row) for row in response["rows"]]
    datasets = [d for d in results if d["dataset_active"]]
    themes = {}
    for d in datasets:
        dataset_themes = d["dataset_themes"].split(";")
        for theme in dataset_themes:
            themes.setdefault(theme, {"dataset": []})
            themes[theme]["dataset"].append(d)

    return templates.TemplateResponse(
        "dataset_index.html",
        {"request": request, "datasets": datasets, "themes": themes},
    )


@router.get("/{dataset}", response_class=HTMLResponse)
async def get_dataset_index(request: Request, dataset: str):
    try:
        _dataset = await get_dataset(dataset)
        typology = specification.field_typology(dataset)
        entities = await EntityQuery().get_entity(
            typology=_dataset[dataset]["typology"], dataset=dataset
        )
        return templates.TemplateResponse(
            "dataset.html",
            {
                "request": request,
                "dataset": _dataset[dataset],
                "entities": entities["rows"],
                "key_field": specification.key_field(typology),
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
