import logging
from typing import Optional, List

from digital_land.view_model import ViewModel
from fastapi import APIRouter, Depends, HTTPException, Request, Query, Header
from fastapi.responses import HTMLResponse, Response
from starlette.responses import JSONResponse
import datetime

from dl_web.data_access.digital_land_queries import (
    get_typologies,
    get_datasets_with_theme,
    get_local_authorities,
)
from dl_web.data_access.entity_queries import EntityQuery, _do_geo_query
from dl_web.data_access.legacy import fetch_entity_metadata, fetch_entity

from dl_web.enum import (
    Suffix,
    PointMatch,
    GeometryMatch,
    EntriesOption,
    DateOption,
)

from dl_web.resources import get_view_model, specification, templates
from dl_web.utils import create_dict

router = APIRouter()
logger = logging.getLogger(__name__)


def geojson_download(
    entity: int,
    entity_snapshot: dict,
):
    if "geojson-full" not in entity_snapshot:
        raise HTTPException(status_code=404, detail="entity has no geometry")

    response = Response(
        entity_snapshot["geojson-full"], media_type="application/geo+json"
    )
    filename = f"{entity}.geojson"
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response


def entity_template_response(
    request: Request,
    entity_snapshot: dict,
    entity_metadata: dict,
    entity_references: dict,
):
    if entity_metadata["dataset"] in specification.typology:
        schema = entity_metadata["dataset"]
    else:
        schema = specification.pipeline[entity_metadata["dataset"]]["schema"]

    return templates.TemplateResponse(
        "row.html",
        {
            "request": request,
            "row": entity_snapshot,
            "entity": None,
            "pipeline_name": entity_metadata["dataset"],
            "references": entity_references,
            # "breadcrumb": slug_to_breadcrumb(slug),
            "breadcrumb": [],
            "schema": schema,
            "typology": entity_metadata["typology"],
            "key_field": specification.key_field(entity_metadata["typology"]),
            "entity_prefix": "",
            "geojson_features": "[%s]" % entity_snapshot.pop("geojson-full")
            if "geojson-full" in entity_snapshot
            else None,
        },
    )


# The order of the router methods is important! This needs to go ahead of /{entity}
@router.get("/{entity}.geojson", response_class=JSONResponse)
def get_entity_as_geojson(
    entity: int,
    view_model: ViewModel = Depends(get_view_model),
):
    entity_metadata: dict = fetch_entity_metadata(view_model, entity)
    entity_snapshot: dict = fetch_entity(view_model, entity, entity_metadata)
    return geojson_download(entity, entity_snapshot)


@router.get("/{entity}", response_class=HTMLResponse)
def get_entity_as_html(
    request: Request,
    entity: int,
    view_model: ViewModel = Depends(get_view_model),
):
    entity_metadata: dict = fetch_entity_metadata(view_model, entity)
    entity_snapshot: dict = fetch_entity(view_model, entity, entity_metadata)
    entity_references = {}

    for reference in view_model.get_references(entity_metadata["typology"], entity):
        entity_references.setdefault(reference["type"], []).append(
            {
                "entity": reference["entity"],
                "reference": reference["reference"],
                "href": f"/entity/{reference['entity']}",
                "text": reference["name"],
            }
        )
    return entity_template_response(
        request, entity_snapshot, entity_metadata, entity_references
    )


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
    theme: Optional[List[str]] = Query(None),
    typology: Optional[List[str]] = Query(None),
    dataset: Optional[List[str]] = Query(None),
    organisation: Optional[List[str]] = Query(None),
    entity: Optional[List[str]] = Query(None),
    curie: Optional[List[str]] = Query(None),
    prefix: Optional[List[str]] = Query(None),
    reference: Optional[List[str]] = Query(None),
    # filter by date
    entries: Optional[EntriesOption] = Query(
        None, description="Results to include current, or all entries"
    ),
    entry_start_date: Optional[datetime.date] = None,
    entry_start_date_year: Optional[str] = None,
    entry_start_date_month: Optional[str] = None,
    entry_start_date_day: Optional[str] = None,
    entry_start_date_match: Optional[DateOption] = None,
    entry_end_date: Optional[datetime.date] = None,
    entry_end_date_year: Optional[str] = None,
    entry_end_date_month: Optional[str] = None,
    entry_end_date_day: Optional[str] = None,
    entry_end_date_match: Optional[DateOption] = None,
    entry_entry_date: Optional[datetime.date] = None,
    entry_entry_date_year: Optional[str] = None,
    entry_entry_date_month: Optional[str] = None,
    entry_entry_date_day: Optional[str] = None,
    entry_entry_date_match: Optional[DateOption] = None,
    # find from a geospatial point
    point_entity: Optional[str] = Query(
        None, description="point from this entity's geometry"
    ),
    point_reference: Optional[str] = Query(
        None, description="point from the entity with this reference"
    ),
    point: Optional[str] = Query(None, description="point in WKT format"),
    longitude: Optional[float] = Query(
        None, description="construct a point with this longitude"
    ),
    latitude: Optional[float] = Query(
        None, description="construct a point with this latitude"
    ),
    point_match: Optional[PointMatch] = Query(None),
    # find from a geospatial multipolygon
    geometry_entity: Optional[str] = Query(
        None, description="take the geometry from this geography entity"
    ),
    geometry_reference: Optional[str] = Query(
        None, description="take the geometry from the geography with this reference"
    ),
    geometry: Optional[str] = Query(None, description="a geometry in WKT format"),
    geometry_match: Optional[GeometryMatch] = None,
    related_entity: Optional[List[str]] = Query(
        None, description="filter by related entity"
    ),
    limit: Optional[int] = Query(
        10, description="limit for the number of results", ge=1
    ),
    next_entity: Optional[int] = Query(
        None, description="paginate results from this entity"
    ),
    accept: Optional[str] = Header(
        None, description="accepted content-type for results"
    ),
    suffix: Optional[Suffix] = Query(None, description="file format for the results"),
):
    query = EntityQuery(
        params={
            "theme": theme,
            "typology": typology,
            "dataset": dataset,
            "organisation": organisation,
            "entity": entity,
            "curie": curie,
            "prefix": prefix,
            "reference": reference,
            "entries": entries,
            "entry_start_date": entry_start_date,
            "entry_start_date_year": entry_start_date_year,
            "entry_start_date_month": entry_start_date_month,
            "entry_start_date_day": entry_start_date_day,
            "entry_start_date_match": entry_start_date_match,
            "entry_end_date": entry_end_date,
            "entry_end_date_year": entry_end_date_year,
            "entry_end_date_month": entry_end_date_month,
            "entry_end_date_day": entry_end_date_day,
            "entry_end_date_match": entry_end_date_match,
            "entry_entry_date": entry_entry_date,
            "entry_entry_date_year": entry_entry_date_year,
            "entry_entry_date_month": entry_entry_date_month,
            "entry_entry_date_day": entry_entry_date_day,
            "entry_entry_date_match": entry_entry_date_match,
            "point_entity": point_entity,
            "point_reference": point_reference,
            "point": point,
            "point_match": point_match,
            "longitude": longitude,
            "latitude": latitude,
            "geometry_entity": geometry_entity,
            "geometry_reference": geometry_reference,
            "geometry": geometry,
            "geometry_match": geometry_match,
            "related_entity": related_entity,
            "next_entity": next_entity,
            "limit": limit,
        }
    )
    data = query.execute()

    if accept == "text/json" or suffix == "json":
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


@router.get("-search", response_class=HTMLResponse)
async def search_entity(
    request: Request,
    longitude: Optional[float] = None,
    latitude: Optional[float] = None,
):
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

    data = []
    if longitude and latitude:
        data = _do_geo_query(longitude, latitude)
    return templates.TemplateResponse(
        "search-facets.html",
        {
            "request": request,
            "data": data,
            "datasets": datasets,
            "local_authorities": local_authorities,
            "typologies": typologies,
        },
    )


@router.get(".geojson", response_class=JSONResponse)
def get_entity_by_long_lat(longitude: float, latitude: float):
    # TBD: redirect or call search
    return _do_geo_query(longitude, latitude)
