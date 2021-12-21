import logging
from datetime import timedelta

from fastapi import FastAPI, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from dl_web.core.templates import templates
from dl_web.data_access.digital_land_queries import fetch_datasets
from dl_web.data_access.entity_queries import fetch_entity_count
from dl_web.routers import entity, dataset, map_, experimental

logger = logging.getLogger(__name__)

SECONDS_IN_TWO_YEARS = timedelta(days=365 * 2).total_seconds()

# Add markdown here
description = """
## About this API
"""

tags_metadata = [
    {
        "name": "Search entity",
        "description": "find entities by location, type or date",
    },
    {
        "name": "Get entity",
        "description": "get entity by id",
    },
    {
        "name": "List datasets",
        "description": "list all datasets",
    },
    {
        "name": "Get dataset",
        "description": "get dataset by id",
    },
]


def create_app():
    app = FastAPI(
        title="Digital land API",
        description=description,
        version="0.1.0",
        contact={
            "name": "Digital land team",
            "email": "#",
        },
        license_info={
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT",
        },
        openapi_tags=tags_metadata,
    )
    add_base_routes(app)
    add_routers(app)
    add_static(app)
    add_middleware(app)
    return app


def add_base_routes(app):
    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    def home(request: Request):
        return templates.TemplateResponse(
            "homepage.html",
            {"request": request},
        )

    @app.get("/health", response_class=JSONResponse, include_in_schema=False)
    async def health(request: Request):
        try:
            datasets = await fetch_datasets()
            entity_count_by_datatset = await fetch_entity_count()
            entity_count = 0
            for ds in entity_count_by_datatset["rows"]:
                entity_count += ds[1]
            return {
                "status": "OK",
                "dataset_count": len(datasets),
                "entity_count": entity_count,
            }

        except Exception as e:
            logger.exception(e)
            raise e

    @app.exception_handler(StarletteHTTPException)
    async def custom_404_exception_handler(
        request: Request, exc: StarletteHTTPException
    ):
        if exc.status_code == 404:
            return templates.TemplateResponse(
                "404.html",
                {"request": request},
                status_code=exc.status_code,
            )
        else:
            # Just use FastAPI's built-in handler for other errors
            return await http_exception_handler(request, exc)

    # catch all handler - for any unhandled exceptions return 500 template
    @app.exception_handler(Exception)
    async def custom_catch_all_exception_handler(request: Request, exc: Exception):
        return templates.TemplateResponse(
            "500.html", {"request": request}, status_code=500
        )


def add_routers(app):

    app.include_router(entity.router, prefix="/entity")
    app.include_router(dataset.router, prefix="/dataset")
    app.include_router(experimental.router, prefix="/experimental")

    # not added to /docs
    app.include_router(map_.router, prefix="/map", include_in_schema=False)


def add_static(app):
    app.mount(
        "/static",
        StaticFiles(directory="static"),
        name="static",
    )


def add_middleware(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def add_strict_transport_security_header(request: Request, call_next):
        response = await call_next(request)
        response.headers[
            "Strict-Transport-Security"
        ] = f"max-age={SECONDS_IN_TWO_YEARS}; includeSubDomains; preload"
        return response

    @app.middleware("http")
    async def add_x_frame_options_header(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "sameorigin"
        return response

    @app.middleware("http")
    async def add_x_content_type_options_header(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response
