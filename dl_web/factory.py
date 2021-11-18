from dl_web.core.resources import templates
from dl_web.routers import entity, dataset, map_

from fastapi import FastAPI, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException


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
    add_static(app)
    return app


def add_base_routes(app):
    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    def home(request: Request):
        return templates.TemplateResponse(
            "homepage.html",
            {"request": request},
        )

    @app.get("/health", response_class=PlainTextResponse, include_in_schema=False)
    def health(request: Request):
        return "OK"

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


def add_routers(app):
    # remove resource until we get to in and decide what's needed
    # app.include_router(resource.router, prefix="/resource")

    app.include_router(entity.router, prefix="/entity")
    app.include_router(dataset.router, prefix="/dataset")

    # map not added to swagger docs page
    app.include_router(map_.router, prefix="/map", include_in_schema=False)


def add_static(app):
    app.mount(
        "/static",
        StaticFiles(directory="static"),
        name="static",
    )
