import logging
import urllib.parse

from digital_land.view_model import ViewModel
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from ..resources import fetch, get_view_model, specification, templates

router = APIRouter()
logger = logging.getLogger(__name__)

# base_url = "http://127.0.0.1/digital-land/"
# base_url = "http://127.0.0.1:8001/digital-land/"
base_url = "http://datasetteawsentityv2-env.eba-gbrdriub.eu-west-2.elasticbeanstalk.com/digital-land/"


async def get_datasets():
    url = f"{base_url}dataset.json?_shape=object"
    logger.info("get_datasets: %s", url)
    return await fetch(url)


async def get_dataset(dataset):
    url = f"{base_url}dataset.json?_shape=object&dataset={urllib.parse.quote(dataset)}"
    logger.info("get_dataset: %s", url)
    return await fetch(url)


@router.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    datasets = await get_datasets()
    return templates.TemplateResponse(
        "dataset_index.html", {"request": request, "datasets": datasets}
    )


@router.get("/{dataset}", response_class=HTMLResponse)
async def get_dataset_index(
    request: Request, dataset: str, view_model: ViewModel = Depends(get_view_model)
):
    try:
        _dataset = await get_dataset(dataset)
        typology = specification.field_typology(
            dataset
        )  # replace this with typology from dataset
        entities = view_model.list_entities(typology, dataset)
        return templates.TemplateResponse(
            "dataset.html",
            {
                "request": request,
                "dataset": _dataset[dataset],
                "entities": entities,
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
