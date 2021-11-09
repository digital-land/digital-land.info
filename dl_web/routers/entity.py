import json
import logging
from dataclasses import asdict

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, Response
from starlette.responses import JSONResponse

from dl_web.data_access.digital_land_queries import (
    get_typologies,
    get_datasets_with_theme,
    get_local_authorities,
)
from dl_web.data_access.entity_queries import EntityQuery

from dl_web.search.filters import (
    BaseFilters,
    DateFilters,
    SpatialFilters,
    PaginationFilters,
    FormatFilters,
)

from dl_web.resources import specification, templates
from dl_web.utils import create_dict

router = APIRouter()
logger = logging.getLogger(__name__)


def geojson_download(entity):
    response = Response(json.dumps(entity["geojson"]))
    filename = f"{entity['entity']}.geojson"
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response


# The order of the router methods is important! This needs to go ahead of /{entity}
@router.get("/{entity}.geojson", response_class=JSONResponse)
async def get_entity_as_geojson(entity: int):
    e = await EntityQuery().get(entity)
    if e is not None and e.get("geojson") is not None:
        return geojson_download(e)
    else:
        raise HTTPException(status_code=404, detail="entity not found")


@router.get("/{entity}", response_class=HTMLResponse)
async def get_entity_as_html(request: Request, entity: int):
    e = await EntityQuery().get(entity)
    if e is not None:
        # TODO - update template - no longer fully works
        return templates.TemplateResponse(
            "entity.html",
            {
                "request": request,
                "row": e,
                "entity": None,
                "pipeline_name": e["dataset"],
                "references": [],
                # "breadcrumb": slug_to_breadcrumb(slug),
                "breadcrumb": [],
                "schema": None,
                "typology": e["typology"],
                "key_field": specification.key_field(e["typology"]),
                "entity_prefix": "",
                "geojson_features": e.get("geojson")
                if e.get("geojson") is not None
                else None,
            },
        )
    else:
        raise HTTPException(status_code=404, detail="entity not found")


@router.get(
    "/",
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
)
async def search(
    request: Request,
    # filter entries
    base_filters: BaseFilters = Depends(BaseFilters),
    date_filters: DateFilters = Depends(DateFilters),
    spatial_filters: SpatialFilters = Depends(SpatialFilters),
    pagination_filters: PaginationFilters = Depends(PaginationFilters),
    format_filters: FormatFilters = Depends(FormatFilters),
):
    base_params = asdict(base_filters)
    date_params = asdict(date_filters)
    spatial_params = asdict(spatial_filters)
    pagination_params = asdict(pagination_filters)
    format_params = asdict(format_filters)

    params = {
        **base_params,
        **date_params,
        **spatial_params,
        **pagination_params,
        **format_params,
    }

    query = EntityQuery(params=params)

    data = query.execute()

    if format_filters.accept == "text/json" or format_filters.suffix == "json":
        return JSONResponse(data)

    # typology facet
    response = await get_typologies()
    typologies = [create_dict(response["columns"], row) for row in response["rows"]]
    # dataset facet
    response = await get_datasets_with_theme()
    dataset_results = [
        create_dict(response["columns"], row) for row in response["rows"]
    ]
    datasets = [d for d in dataset_results if d["dataset_active"]]
    # local-authority-district facet
    response = await get_local_authorities()
    local_authorities = [
        create_dict(response["columns"], row) for row in response["rows"]
    ]

    # default is HTML
    return templates.TemplateResponse(
        "search.html",
        {
            "request": request,
            "data": data,
            "datasets": datasets,
            "local_authorities": local_authorities,
            "typologies": typologies,
            "query": query,
            "active_filters": [
                filter_name
                for filter_name, values in query.params.items()
                if filter_name != "limit" and values is not None
            ],
        },
    )
