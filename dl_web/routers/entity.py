import logging
from typing import Optional, List

from digital_land.entity_lookup import lookup_by_slug
from digital_land.view_model import ViewModel
from fastapi import APIRouter, Depends, HTTPException, Request, Query, Header
from fastapi.responses import HTMLResponse, Response
from starlette.responses import JSONResponse
import datetime

from dl_web.queries import EntityQuery, _do_geo_query

from dl_web.enum import (
    Suffix,
    PointMatch,
    GeometryMatch,
    EntriesOption,
    DateOption,
)

from dl_web.resources import get_view_model, specification, templates

from ..resources import fetch
from ..utils import create_dict

router = APIRouter()
logger = logging.getLogger(__name__)

datasette_url = "https://datasette.digital-land.info/"


async def get_typologies():
    url = f"{datasette_url}digital-land/typology.json"
    logger.info("get_typologies: %s", url)
    return await fetch(url)


async def get_datasets_with_theme():
    url = "".join(
        (
            f"{datasette_url}digital-land.json?sql=SELECT%0D%0A++DISTINCT+",
            "dataset.dataset%2C%0D%0A++dataset.name%2C%0D%0A++dataset.plural%2C%0D%0A++dataset.typology",
            "%2C%0D%0A++%28%0D%0A++++CASE%0D%0A++++++WHEN+pipeline.pipeline+IS+NOT+NULL+THEN+1%0D%0A++++++",
            "WHEN+pipeline.pipeline+IS+NULL+THEN+0%0D%0A++++END%0D%0A++%29+AS+dataset_active%2C%0D%0A++GROUP_CONCAT",
            "%28dataset_theme.theme%2C+%22%3B%22%29+AS+dataset_themes%0D%0AFROM%0D%0A++dataset%0D%0A++LEFT+JOIN+",
            "pipeline+ON+dataset.dataset+%3D+pipeline.pipeline%0D%0A++INNER+JOIN+dataset_theme+ON+dataset.dataset+",
            "%3D+dataset_theme.dataset%0D%0Agroup+by%0D%0A++dataset.dataset%0D%0Aorder+by%0D%0Adataset.name+ASC",
        )
    )
    logger.info("get_datasets_with_themes: %s", url)
    return await fetch(url)


async def get_local_authorities():
    url = "".join(
        (
            f"{datasette_url}digital-land.json?sql=select%0D%0A++addressbase_custodian%2C%0D%0A++billing_authority",
            "%2C%0D%0A++census_area%2C%0D%0A++combined_authority%2C%0D%0A++company%2C%0D%0A++end_date%2C%0D%0A++entity",
            "%2C%0D%0A++entry_date%2C%0D%0A++esd_inventory%2C%0D%0A++local_authority_type%2C%0D%0A++",
            "local_resilience_forum%2C%0D%0A++name%2C%0D%0A++official_name%2C%0D%0A++opendatacommunities_area",
            "%2C%0D%0A++opendatacommunities_organisation%2C%0D%0A++organisation%2C%0D%0A++region",
            "%2C%0D%0A++shielding_hub%2C%0D%0A++start_date%2C%0D%0A++statistical_geography%2C%0D%0A++twitter",
            "%2C%0D%0A++website%2C%0D%0A++wikidata%2C%0D%0A++wikipedia%0D%0Afrom%0D%0A++organisation%0D%0Awhere",
            "%0D%0A++%22organisation%22+like+%22%25local-authority-eng%25%22%0D%0Aorder+by%0D%0A++organisation%0D%0A&p0",
            "=%25local-authority-eng%25",
        )
    )
    logger.info("get_local_authorities: %s", url)
    return await fetch(url)


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
    entry_start_date_year: Optional[int] = None,
    entry_start_date_month: Optional[int] = None,
    entry_start_date_day: Optional[int] = None,
    entry_start_date_match: Optional[DateOption] = None,
    entry_end_date: Optional[datetime.date] = None,
    entry_end_date_year: Optional[int] = None,
    entry_end_date_month: Optional[int] = None,
    entry_end_date_day: Optional[int] = None,
    entry_end_date_match: Optional[DateOption] = None,
    entry_entry_date: Optional[datetime.date] = None,
    entry_entry_date_year: Optional[int] = None,
    entry_entry_date_month: Optional[int] = None,
    entry_entry_date_day: Optional[int] = None,
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
def get_entity_by_long_lat(
    longitude: float,
    latitude: float,
):
    # TBD: redirect or call search
    return _do_geo_query(longitude, latitude)
