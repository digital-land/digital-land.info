import logging
from dataclasses import asdict
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse

from application.core.models import GeoJSONFeatureCollection, EntityModel
from application.data_access.digital_land_queries import (
    get_datasets,
    get_local_authorities,
    get_typologies,
)
from application.data_access.entity_queries import get_entity_query, get_entity_search

from application.search.enum import Suffix
from application.search.filters import QueryFilters
from application.core.templates import templates
from application.core.utils import DigitalLandJSONResponse

router = APIRouter()
logger = logging.getLogger(__name__)


def _get_geojson(data: List[EntityModel]) -> GeoJSONFeatureCollection:
    results = [item.geojson for item in data]
    return {"type": "FeatureCollection", "features": results}


def get_entity(request: Request, entity: int, extension: Optional[Suffix] = None):

    e = get_entity_query(entity)
    if e is not None:

        if extension is not None and extension.value == "json":
            return e

        if extension is not None and extension.value == "geojson":
            return e.geojson

        return templates.TemplateResponse(
            "entity.html",
            {
                "request": request,
                "row": e.dict(by_alias=True, exclude={"geojson"}),
                "entity": e.dict(by_alias=True, exclude={"geojson"}),
                "pipeline_name": e.dataset,
                "references": [],
                "breadcrumb": [],
                "schema": None,
                "typology": e.typology,
                "entity_prefix": "",
                "geojson_features": e.geojson if e.geojson is not None else None,
            },
        )
    else:
        raise HTTPException(status_code=404, detail="entity not found")


def make_pagination_link(query_params, offset):
    url = "?" + "&".join(
        [
            "{}={}".format(param[0], param[1])
            for param in query_params
            if param[0] != "offset"
        ]
    )
    return url + "&offset={}".format(offset)


def search_entities(
    request: Request,
    query_filters: QueryFilters = Depends(),
    extension: Optional[Suffix] = None,
):
    query_params = asdict(query_filters)
    data = get_entity_search(query_params)

    # the query does some normalisation to remove empty
    # params and they get returned from search
    params = data["params"]

    if extension is not None and extension.value == "json":
        return data["entities"]

    if extension is not None and extension.value == "geojson":
        return _get_geojson(data["entities"])

    # typology facet
    typologies = get_typologies()
    typologies = [t.dict() for t in typologies]
    # dataset facet
    response = get_datasets()
    columns = ["dataset", "name", "plural", "typology", "themes"]
    datasets = [dataset.dict(include=set(columns)) for dataset in response]

    local_authorities = get_local_authorities()
    local_authorities = [la.dict() for la in local_authorities]

    if params.get("offset") is not None:
        offset = params["offset"] + params["limit"]
    else:
        offset = params["limit"]
    next_url = (
        make_pagination_link(request.query_params._list, offset) if data else None
    )

    # default is HTML
    return templates.TemplateResponse(
        "search.html",
        {
            "request": request,
            "count_all": data["count_all"],
            "data": data["entities"],
            "datasets": datasets,
            "local_authorities": local_authorities,
            "typologies": typologies,
            "query": {"params": params},
            "active_filters": [
                filter_name
                for filter_name, values in params.items()
                if filter_name != "limit" and values is not None
            ],
            "url_query_params": {
                "str": ("&").join(
                    [
                        "{}={}".format(param[0], param[1])
                        for param in request.query_params._list
                    ]
                ),
                "list": request.query_params._list,
            },
            "next_url": next_url,
        },
    )


# Route ordering in important. Match routes with extensions first
router.add_api_route(
    ".{extension}",
    endpoint=search_entities,
    response_class=DigitalLandJSONResponse,
    tags=["Search entity"],
)
router.add_api_route(
    "/",
    endpoint=search_entities,
    responses={
        200: {
            "content": {
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {},
                "application/zip": {},
                "application/x-qgis-project": {},
                "application/geo+json": {},
                "text/json": {},
                "text/csv": {},
                "text/turtle": {},
            },
            "description": "List of entities in one of a number of different formats.",
        }
    },
    response_class=HTMLResponse,
    include_in_schema=False,
)

router.add_api_route(
    "/{entity}.{extension}",
    get_entity,
    response_class=DigitalLandJSONResponse,
    tags=["Get entity"],
)
router.add_api_route(
    "/{entity}",
    endpoint=get_entity,
    response_class=HTMLResponse,
    include_in_schema=False,
)
