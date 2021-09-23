import asyncio
import logging
import logging.config
import os
import time

import uvicorn
import yaml
from fastapi import Depends, FastAPI, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from dl_web.data_store import get_datastore

from .resources import get_view_model, proxy, specification, templates
from .routers import entity, resource, dataset, map_

with open("log_config.yml") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    logging.config.dictConfig(config)

logger = logging.getLogger(__name__)


async def refresh_collection(fetch):
    datastore = await get_datastore()
    if fetch:
        global last_refresh
        last_refresh = time.time()
        await datastore.fetch_collections(
            specification.schema_field, set(specification.pipeline.keys())
        )
    await datastore.close_connection()


async def core_startup():
    logger.debug("core startup")
    fetch = os.getenv("FETCH", "True").lower() not in ["0", "false", "f", "n", "no"]
    logger.info(f'Fetch is {"enabled" if fetch else "disabled"}')
    await refresh_collection(fetch)


async def worker_startup():
    logger.debug("worker startup")
    datastore = await get_datastore()
    # reinitialise the aiohttp.ClientSession so it uses the fastapi event loop
    await datastore._async_init()
    datastore.load_collection()


def create_app():
    app = FastAPI(
        title="Digital-Land Data API",
        description="API and website for Digital-Land data",
        version="0.9",
        dependencies=[Depends(get_view_model)],
        on_startup=[worker_startup],
    )
    asyncio.run(core_startup())
    return app


app = create_app()
last_refresh = None


app.include_router(resource.router, prefix="/resource")
app.include_router(entity.router, prefix="/entity")
app.include_router(dataset.router, prefix="/dataset")
app.include_router(map_.router, prefix="/map")
app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static",
)

# the base templates expect images to be served at /images
app.mount(
    "/images",
    StaticFiles(directory="static/govuk/assets/images"),
    name="images",
)


# @app.on_event("shutdown")
# def on_stopping():
#     # I don't think this is actually firing. Needs investigation
#     datastore = get_datastore()
#     datastore.close_connections()


# Show the standard page for 404
@app.exception_handler(StarletteHTTPException)
async def custom_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return templates.TemplateResponse(
            "404.html",
            {"request": request},
            status_code=404,
        )
    else:
        # Just use FastAPI's built-in handler for other errors
        return await http_exception_handler(request, exc)


@app.get("/health", response_class=PlainTextResponse)
def health(request: Request):
    return "OK"


@app.get("/{something:path}/")
async def proxy_guidance(request: Request, something: str, response_class=HTMLResponse):
    return HTMLResponse(await proxy(f"http://digital-land.github.io/{something}/"))


# My attempt at allowing refresh via http. Just get rid and use the DB!
#
# @app.get("/refresh")
# def refresh(request: Request, background_tasks: BackgroundTasks):
#     if last_refresh and time.time() - last_refresh < 60:
#         return Response(status_code=403, content="too soon")

#     background_tasks.add_task(refresh_collection(True))
#     return Response(status_code=202, content="refreshing data", media_type="text/plain")


# A route to return status info about the server. Not used for now.
#
# @app.get("/status")
# def status(request: Request):
#     human_readable_refreshed = (
#         datetime.datetime.fromtimestamp(last_refresh).isoformat()
#         if last_refresh
#         else None
#     )
#     return JSONResponse(
#         status_code=200,
#         content={"last_refresh": human_readable_refreshed},
#     )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
