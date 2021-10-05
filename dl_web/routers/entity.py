import logging

from digital_land.entity_lookup import lookup_by_slug
from digital_land.view_model import ViewModel
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from starlette.responses import JSONResponse

from ..resources import get_view_model, specification, templates

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


@router.get("/", response_class=RedirectResponse)
def get_entity_by_slug(
    request: Request,
    slug: str,
):
    entity = lookup_entity(slug)
    return RedirectResponse(
        status_code=301, url=request.url_for("get_entity_as_html", entity=entity)
    )
