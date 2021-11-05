import logging
from typing import Optional, List

from digital_land.entity_lookup import lookup_by_slug
from digital_land.view_model import ViewModel
from fastapi import APIRouter, Depends, HTTPException, Request, Query, Header
from fastapi.responses import HTMLResponse, Response
from starlette.responses import JSONResponse

from dl_web.queries import EntityQuery, _do_geo_query
from dl_web.resources import get_view_model, specification, templates

router = APIRouter()
logger = logging.getLogger(__name__)


def fetch_entity_metadata(
    view_model: ViewModel,
    entity: int,
) -> dict:
    metadata = view_model.get_entity_metadata(entity)
    if not metadata:
        raise HTTPException(status_code=404, detail="entity not found")
    return metadata


def fetch_entity(
    view_model: ViewModel,
    entity: int,
    entity_metadata: dict,
) -> dict:
    try:
        entity_snapshot = view_model.get_entity(entity_metadata["typology"], entity)
    except (AssertionError, KeyError):
        entity_snapshot = None

    if not entity_snapshot:
        raise HTTPException(status_code=404, detail="entity not found")

    entity_snapshot = {
        k.replace("_", "-"): v
        for k, v in entity_snapshot.items()
        if v and k not in ("geometry")
    }

    return entity_snapshot


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


def lookup_entity(slug: str) -> int:
    try:
        entity = lookup_by_slug(slug)
    except ValueError as err:
        logger.warning("lookup_by_slug failed: %s", err)
        raise HTTPException(status_code=404, detail="slug lookup failed")

    return entity


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
def search(
    request: Request,
    # filter entries
    theme: Optional[List[str]] = Query(None),
    typology: Optional[List[str]] = Query(None),
    dataset: Optional[List[str]] = Query(None),
    organisation: Optional[List[str]] = Query(None),
    entity: Optional[List[str]] = Query(None),
    reference: Optional[List[str]] = Query(None),
    # filter by entry date
    entries: Optional[str] = None,  # all* | current | historical
    # fine-grained dates
    entry_start_date: Optional[str] = None,
    entry_end_date: Optional[str] = None,
    entry_entry_date: Optional[str] = None,
    entry_start_date_match: Optional[str] = None,  # match* | before | after
    entry_end_date_match: Optional[str] = None,  # match* | before | after
    entry_entry_date_match: Optional[str] = None,  # match* | before | after
    # find from a geospatial point
    point_entity: Optional[str] = Query(
        None, description="point from this entity's geometry"
    ),
    point_reference: Optional[str] = Query(
        None, description="point from the entity with this reference"
    ),
    longitude: Optional[float] = Query(
        None, description="construct a point with this longitude"
    ),
    latitude: Optional[float] = Query(
        None, description="construct a point with this latitude"
    ),
    point: Optional[str] = Query(None, descrition="point as WKT"),
    point_match: Optional[str] = Query(None),  # within* |
    # find from a geospatial multipolygon
    geometry_reference: Optional[str] = None,  # entity to take MULTIPOLYGON from
    geometry_entity: Optional[str] = None,  # entity to take MULTIPOLYGON from
    geometry: Optional[str] = None,  # WKT multipolygon
    geometry_match: Optional[
        str
    ] = None,  # intersects | within | contains | overlaps | etc
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
    suffix: Optional[str] = Query(None, description="file format of the results"),
):
    query = EntityQuery(
        params={
            "theme": theme,
            "typology": typology,
            "dataset": dataset,
            "organisation": organisation,
            "entity": entity,
            "reference": reference,
            "entries": entries,
            "entry_start_date": entry_start_date,
            "entry_end_date": entry_end_date,
            "entry_entry_date": entry_entry_date,
            "entry_start_date_match": entry_start_date_match,
            "entry_end_date_match": entry_end_date_match,
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

    # default is HTML
    return templates.TemplateResponse("search.html", {"request": request, "data": data})


@router.get(".geojson", response_class=JSONResponse)
def get_entity_by_long_lat(
    longitude: float,
    latitude: float,
):
    # TBD: redirect or call search
    return _do_geo_query(longitude, latitude)
