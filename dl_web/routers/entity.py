import json
import logging
from typing import Optional

from digital_land.entity_lookup import lookup_by_slug
from digital_land.view_model import ViewModel
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, Response
from starlette.responses import JSONResponse

from dl_web.queries import EntityGeoQuery
from dl_web.resources import get_view_model, specification, templates

from ..resources import fetch

router = APIRouter()
logger = logging.getLogger(__name__)

datasette_url = "https://datasette.digital-land.info/"


def create_dict(keys_list, values_list):
    zip_iterator = zip(keys_list, values_list)
    return dict(zip_iterator)


async def get_typologies():
    url = f"{datasette_url}digital-land/typology.json"
    logger.info("get_typologies: %s", url)
    return await fetch(url)


async def get_datasets_with_theme():
    url = f"{datasette_url}digital-land.json?sql=SELECT%0D%0A++DISTINCT+dataset.dataset%2C%0D%0A++dataset.name%2C%0D%0A++dataset.plural%2C%0D%0A++dataset.typology%2C%0D%0A++%28%0D%0A++++CASE%0D%0A++++++WHEN+pipeline.pipeline+IS+NOT+NULL+THEN+1%0D%0A++++++WHEN+pipeline.pipeline+IS+NULL+THEN+0%0D%0A++++END%0D%0A++%29+AS+dataset_active%2C%0D%0A++GROUP_CONCAT%28dataset_theme.theme%2C+%22%3B%22%29+AS+dataset_themes%0D%0AFROM%0D%0A++dataset%0D%0A++LEFT+JOIN+pipeline+ON+dataset.dataset+%3D+pipeline.pipeline%0D%0A++INNER+JOIN+dataset_theme+ON+dataset.dataset+%3D+dataset_theme.dataset%0D%0Agroup+by%0D%0A++dataset.dataset%0D%0Aorder+by%0D%0Adataset.name+ASC"
    logger.info("get_datasets_with_themes: %s", url)
    return await fetch(url)


async def get_local_authorities():
    url = f"{datasette_url}digital-land.json?sql=select%0D%0A++addressbase_custodian%2C%0D%0A++billing_authority%2C%0D%0A++census_area%2C%0D%0A++combined_authority%2C%0D%0A++company%2C%0D%0A++end_date%2C%0D%0A++entity%2C%0D%0A++entry_date%2C%0D%0A++esd_inventory%2C%0D%0A++local_authority_type%2C%0D%0A++local_resilience_forum%2C%0D%0A++name%2C%0D%0A++official_name%2C%0D%0A++opendatacommunities_area%2C%0D%0A++opendatacommunities_organisation%2C%0D%0A++organisation%2C%0D%0A++region%2C%0D%0A++shielding_hub%2C%0D%0A++start_date%2C%0D%0A++statistical_geography%2C%0D%0A++twitter%2C%0D%0A++website%2C%0D%0A++wikidata%2C%0D%0A++wikipedia%0D%0Afrom%0D%0A++organisation%0D%0Awhere%0D%0A++%22organisation%22+like+%22%25local-authority-eng%25%22%0D%0Aorder+by%0D%0A++organisation%0D%0A&p0=%25local-authority-eng%25"
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


@router.get("/{entity}/field/{field}/provenance", response_class=HTMLResponse)
def get_entity_field_provenance_as_html(
    request: Request,
    entity: int,
    field: str,
    view_model: ViewModel = Depends(get_view_model),
):
    return templates.TemplateResponse(
        "field_provenance.html",
        {
            "request": request,
            "entity": entity,
            "field": field,
            "breadcrumb": [],
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


@router.get("/", response_class=HTMLResponse)
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
    print("local authority districts: ", len(local_authorities))

    data = []
    print(request.query_params["test"])
    for param, v in request.query_params.items():
        print("param", param)
    if longitude and latitude:
        data = _do_geo_query(longitude, latitude)
    return templates.TemplateResponse(
        "search.html",
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
    return _do_geo_query(longitude, latitude)


class EntityJson:
    @staticmethod
    def to_json(data):
        fields = [
            "dataset",
            "entry_date",
            "reference",
            "entity",
            "reference",
            "name",
            "geojson",
            "typology",
        ]
        data_dict = {}
        for key, val in data.items():
            if key in fields:
                v = json.loads(val) if key == "geojson" else val
                data_dict[key] = v
        return data_dict


def _do_geo_query(longitude: float, latitude: float):
    data = EntityGeoQuery().execute(longitude, latitude)
    results = []
    for row in data.get("rows", []):
        results.append(EntityJson.to_json(row))
    resp = {
        "query": {"longitude": longitude, "latitude": latitude},
        "count": len(results),
        "results": results,
    }
    return resp
