import logging

from digital_land.view_model import ViewModel
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse

from ..resources import get_view_model, specification, templates

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/{type_}/{slug:path}", response_class=HTMLResponse)
def slug(
    request: Request,
    type_: str,
    slug: str,
    view_model: ViewModel = Depends(get_view_model),
):

    # TODO:
    # - breadcrumb
    # - asyncio for simultaneous http requests to view model (base + refs)

    try:
        typology = specification.field_typology(type_)
        key = f"/{type_}/{slug}"
        entity_snapshot = view_model.get_typology_entity_by_slug(typology, key)
    except (AssertionError, KeyError):
        raise HTTPException(status_code=404, detail="entity not found")

    entity_snapshot = {
        k.replace("_", "-"): v
        for k, v in entity_snapshot.items()
        if v and k not in ("geometry")
    }

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
