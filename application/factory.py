import logging
import sentry_sdk

from datetime import timedelta

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from http import HTTPStatus

from application.core.templates import templates
from application.db.models import EntityOrm
from application.exceptions import DigitalLandValidationError
from application.routers import (
    entity,
    dataset,
    map_,
    curie,
    organisation,
    fact,
    guidance_,
    about_,
)
from application.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

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
        title="planning.data.gov.uk API",
        description=description,
        version="0.1.0",
        contact={
            "name": "planning.data.gov.uk team",
            "email": "digitalland@levellingup.gov.uk",
            "url": "https://www.planning.data.gov.uk",
        },
        license_info={
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT",
        },
        openapi_tags=tags_metadata,
        docs_url=None,
        redoc_url=None,
        servers=[{"url": "https://www.planning.data.gov.uk"}],
    )
    add_base_routes(app)
    add_routers(app)
    add_static(app)
    app = add_middleware(app)
    return app


def add_base_routes(app):
    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    def home(request: Request):
        return templates.TemplateResponse(
            "homepage.html", {"request": request, "opengraph_image": True}
        )

    @app.get("/health", response_class=JSONResponse, include_in_schema=False)
    def health():
        from application.db.session import get_context_session
        from sqlalchemy.sql import select

        try:
            with get_context_session() as session:
                sql = select(EntityOrm.entity).limit(1)
                result = session.execute(sql).fetchone()
                status = {
                    "status": "OK",
                    "entities_present": "OK" if result is not None else "FAIL",
                }
                logger.info(f"healthcheck {status}")
                return status
        except Exception as e:
            logger.exception(e)
            raise e

    @app.get(
        "/invalid-geometries", response_class=JSONResponse, include_in_schema=False
    )
    def invalid_geometries():

        from application.db.session import get_context_session
        from application.core.models import entity_factory
        from sqlalchemy import func
        from sqlalchemy import and_
        from sqlalchemy import not_

        try:
            with get_context_session() as session:
                query_args = [
                    EntityOrm,
                    func.ST_IsValidReason(EntityOrm.geometry).label("invalid_reason"),
                ]
                query = session.query(*query_args)
                query = query.filter(
                    and_(
                        EntityOrm.geometry.is_not(None),
                        not_(func.ST_IsValid(EntityOrm.geometry)),
                    )
                )
                entities = query.all()
                return [
                    {
                        "entity": entity_factory(e.EntityOrm),
                        "invalid_reason": e.invalid_reason,
                    }
                    for e in entities
                ]
        except Exception as e:
            logger.exception(e)
            return {"message": "There was an error checking for invalid geometries"}

    @app.get("/cookies", response_class=HTMLResponse, include_in_schema=False)
    def cookies(request: Request):
        return templates.TemplateResponse(
            "pages/cookies.html",
            {"request": request},
        )

    @app.get(
        "/accessibility-statement", response_class=HTMLResponse, include_in_schema=False
    )
    def accessibility_statement(request: Request):
        return templates.TemplateResponse(
            "pages/accessibility-statement.html",
            {"request": request},
        )

    @app.get("/docs", response_class=HTMLResponse, include_in_schema=False)
    def docs(request: Request):
        open_api_dict = app.openapi()
        return templates.TemplateResponse(
            "pages/docs.html",
            {
                "request": request,
                "paths": open_api_dict["paths"],
                "components": open_api_dict["components"],
            },
        )

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

    # FastAPI disapproves of handling ValidationErrors as they leak internal info to users
    # Unfortunately, the errors raised by the validator bound to QueryFilters are not caught and
    # reraised as RequestValidationError, so we handle that subset of ValidationErrors manually here
    @app.exception_handler(ValidationError)
    async def custom_validation_error_handler(request: Request, exc: ValidationError):
        if all(
            [
                isinstance(raw_error.exc, DigitalLandValidationError)
                for raw_error in exc.raw_errors
            ]
        ):
            try:
                extension_path_param = request.path_params["extension"]
            except KeyError:
                extension_path_param = None
            if extension_path_param in ["json", "geojson"]:
                return JSONResponse(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    content=jsonable_encoder({"detail": exc.errors()}),
                )
            else:
                return templates.TemplateResponse(
                    "404.html",
                    {"request": request},
                    status_code=status.HTTP_404_NOT_FOUND,
                )

        else:
            raise exc

    @app.exception_handler(RequestValidationError)
    async def custom_request_validation_error_handler(request, exc):
        try:
            extension_path_param = request.path_params["extension"]
        except KeyError:
            extension_path_param = None

        if extension_path_param in ["json", "geojson"]:
            return JSONResponse(
                status_code=422,
                content=jsonable_encoder({"detail": exc.errors()}),
            )
        else:
            return templates.TemplateResponse(
                "404.html", {"request": request}, status_code=404
            )

    # catch all handler - for any unhandled exceptions return 500 template
    @app.exception_handler(Exception)
    async def custom_catch_all_exception_handler(request: Request, exc: Exception):
        return templates.TemplateResponse(
            "500.html", {"request": request}, status_code=500
        )


def add_routers(app):

    app.include_router(entity.router, prefix="/entity")
    app.include_router(dataset.router, prefix="/dataset")
    app.include_router(curie.router, prefix="/curie")
    app.include_router(curie.router, prefix="/prefix")
    app.include_router(organisation.router, prefix="/organisation")
    app.include_router(fact.router, prefix="/fact")

    # not added to /docs
    app.include_router(map_.router, prefix="/map", include_in_schema=False)
    app.include_router(guidance_.router, prefix="/guidance", include_in_schema=False)
    app.include_router(about_.router, prefix="/about", include_in_schema=False)


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

    # this has to registered after the first middleware but before sentry?
    app.add_middleware(SuppressClientDisconnectNoResponseReturnedMiddleware)

    if settings.SENTRY_DSN:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.ENVIRONMENT,
            traces_sample_rate=settings.SENTRY_TRACE_SAMPLE_RATE,
            release=settings.RELEASE_TAG,
        )
        app.add_middleware(SentryAsgiMiddleware)

    return app


# Supress "no response returned" error when client disconnects
# discussion and sample code found here
# https://github.com/encode/starlette/discussions/1527
class SuppressClientDisconnectNoResponseReturnedMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        try:
            response = await call_next(request)
        except RuntimeError as e:
            if await request.is_disconnected() and str(e) == "No response returned.":
                logger.warning(
                    "Error 'No response returned' detected - but client already disconnected"
                )
                return Response(status_code=HTTPStatus.NO_CONTENT)
            else:
                raise
        return response
