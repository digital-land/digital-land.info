import datetime
import logging.config
import os
import time

import uvicorn
import yaml
from fastapi import BackgroundTasks, Depends, FastAPI, Request, Response
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from dl_web.data_store import datastore

from .resources import get_view_model, specification, templates
from .routers import resource, slug

with open("log_config.yml") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    logging.config.dictConfig(config)

logger = logging.getLogger(__name__)
app = FastAPI(dependencies=[Depends(get_view_model)])
last_refresh = None


@app.on_event("startup")
async def on_starting():
    logger.warning("----> WORKER STARTUP")
    logger.debug("Running on_starting hook")
    fetch = os.getenv("FETCH", "True").lower() not in ["0", "false", "f", "n", "no"]
    logger.info(f'Fetch is {"enabled" if fetch else "disabled"}')
    if fetch:
        await refresh_data()


# spec = Specification("specification")
app.include_router(resource.router, prefix="/resource")
app.include_router(slug.router, prefix="/slug")
app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static",
)

logger.warn("------> ROOT WORKER STARTUP")


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


@app.get("/health")
def health(request: Request):
    return Response(content="OK", media_type="text/plain")


@app.get("/refresh")
def refresh(request: Request, background_tasks: BackgroundTasks):
    if last_refresh and time.time() - last_refresh < 60:
        return Response(status_code=403, content="too soon")

    background_tasks.add_task(refresh_data)
    return Response(status_code=202, content="refreshing data", media_type="text/plain")


@app.get("/status")
def status(request: Request):
    human_readable_refreshed = (
        datetime.datetime.fromtimestamp(last_refresh).isoformat()
        if last_refresh
        else None
    )
    return JSONResponse(
        status_code=200,
        content={"last_refresh": human_readable_refreshed},
    )


async def refresh_data():
    global last_refresh
    last_refresh = time.time()
    await datastore.fetch_collections(
        specification.schema_field, set(specification.pipeline.keys())
    )


# Development mode: `python -m dl_web.app`
if __name__ == "__main__":
    # on_starting(app)
    datastore.load_collection()
    uvicorn.run("dl_web.app:app", host="0.0.0.0", port=80, reload=True, workers=5)
