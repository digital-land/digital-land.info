import logging
from typing import Optional

from digital_land.view_model import ViewModel
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, Response

from ..resources import get_view_model, specification, templates

router = APIRouter()
logger = logging.getLogger(__name__)


def get_typology(type_: str):
    return specification.field_typology(type_)


def fetch_entity(
    type_: str,
    key: str,
    typology: str = Depends(get_typology),
    view_model: ViewModel = Depends(get_view_model),
):
    try:
        slug = f"/{type_}/{key}"
        entity_snapshot = view_model.get_typology_entity_by_slug(typology, slug)
    except (AssertionError, KeyError):
        raise HTTPException(status_code=404, detail="entity not found")

    entity_snapshot = {
        k.replace("_", "-"): v
        for k, v in entity_snapshot.items()
        if v and k not in ("geometry")
    }

    return entity_snapshot


def geojson_download(
    key: str,
    entity_snapshot: dict,
):
    if "geojson-full" not in entity_snapshot:
        raise HTTPException(status_code=404, detail="entity has no geometry")

    response = Response(
        entity_snapshot["geojson-full"], media_type="application/geo+json"
    )
    filename = key.split("/")[-1] + ".geojson"
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response


@router.get("/{type_}/{key:path}", response_class=HTMLResponse)
def slug(
    request: Request,
    type_: str,
    key: str,
    format: Optional[str] = None,
    typology: str = Depends(get_typology),
    entity_snapshot=Depends(fetch_entity),
):

    # TODO:
    # - breadcrumb
    # - asyncio for simultaneous http requests to view model (base + refs)
    # - implement download geojson link

    if format == "geojson":
        return geojson_download(key, entity_snapshot)

    if format:
        raise HTTPException(status_code=404, detail="unsupported format")

    return templates.TemplateResponse(
        "row.html",
        {
            "request": request,
            "row": entity_snapshot,
            "entity": None,
            "pipeline_name": type_,
            "breadcrumb": [],
            "schema": specification.pipeline[type_]["schema"],
            "typology": typology,
            "key_field": specification.key_field(typology),
            "entity_prefix": "/slug",
            "geojson_features": f"[{(entity_snapshot.pop('geojson-full', None))}]",
        },
    )
