import logging.config
import os

import uvicorn
import yaml
from digital_land.specification import Specification
from fastapi import FastAPI, Request, Response
from fastapi.exception_handlers import http_exception_handler
from starlette.exceptions import HTTPException as StarletteHTTPException

from dl_web.data_store import datastore

from .resources import templates
from .routers import resource

with open("log_config.yml") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    logging.config.dictConfig(config)

logger = logging.getLogger(__name__)
app = FastAPI()


def on_starting(server):
    logger.debug("Running on_starting hook")
    fetch = os.getenv("FETCH", "True").lower() not in ["0", "false", "f", "n", "no"]
    logger.info(f'Fetch is {"enabled" if fetch else "disabled"}')
    if fetch:
        datastore.fetch_collections(spec.schema_field, set(spec.pipeline.keys()))


spec = Specification("specification")
app.include_router(resource.router)


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


@app.route("/health")
def health(request: Request):
    return Response(content="OK", media_type="text/plain")


# Development mode: `python -m dl_web.app`
if __name__ == "__main__":
    on_starting(app)
    datastore.load_collection()
    uvicorn.run("dl_web.app:app", host="0.0.0.0", port=80, reload=True)
