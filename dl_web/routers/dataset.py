import logging

import aiohttp
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse

from ..resources import get_view_model, specification, templates

router = APIRouter()
logger = logging.getLogger(__name__)

# base_url = "http://127.0.0.1/digital-land/"
base_url = "http://datasetteawsentityv2-ecr-env.eba-gbrdriub.eu-west-2.elasticbeanstalk.com/digital-land/"


async def get_datasets():
    url = f"{base_url}dataset.json?_shape=object"
    logger.info("get_datasets: %s", url)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            logger.info(resp.status)
            return await resp.json()


@router.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    datasets = await get_datasets()
    return templates.TemplateResponse(
        "dataset_index.html", {"request": request, "datasets": datasets}
    )


@router.get("/{dataset}", response_class=HTMLResponse)
def get_dataset_index(request: Request, dataset: str):
    return templates.TemplateResponse("dataset.html", {"request": request})
