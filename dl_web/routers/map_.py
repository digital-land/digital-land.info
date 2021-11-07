import logging

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from dl_web.resources import templates

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_class=HTMLResponse)
def get_map(request: Request):
    all_layers = [
        {
            "dataset": "local-authority-district",
            "label": "Local authority districts",
            "paint_options": {"colour": "#0b0c0c", "opacity": "0.1", "weight": 5},
        },
        {
            "dataset": "conservation-area",
            "label": "Conservation areas",
            "paint_options": {
                "colour": "#78AA00",
            },
        },
        {
            "dataset": "brownfield-land",
            "label": "Brownfield land",
            "paint_options": {
                "colour": "#745729",
            },
            "type": "point",
        },
        {
            "dataset": "parish",
            "label": "Parishes",
            "paint_options": {
                "colour": "#5694ca",
            },
        },
        {
            "dataset": "heritage-coast",
            "label": "Heritage coast",
            "paint_options": {
                "colour": "#912b88",
            },
        },
        {
            "dataset": "area-of-outstanding-natural-beauty",
            "label": "Areas of outstanding natural beauty",
            "paint_options": {
                "colour": "#d53880",
            },
        },
        {
            "dataset": "ancient-woodland",
            "label": "Ancient woodland",
            "paint_options": {"colour": "#00703c", "opacity": 0.2},
        },
        {
            "dataset": "green-belt",
            "label": "Green belt",
            "paint_options": {"colour": "#85994b"},
        },
        {
            "dataset": "world-heritage-site",
            "label": "World heritage site",
            "paint_options": {
                "colour": "#012169",
            },
        },
        {
            "dataset": "battlefield",
            "label": "Battlefields",
            "paint_options": {"colour": "#4d2942", "opacity": 0.2},
        },
        {
            "dataset": "park-and-garden",
            "label": "Parks and gardens",
            "paint_options": {
                "colour": "#0EB951",
            },
        },
        {
            "dataset": "protected-wreck-site",
            "label": "Protected wreck sites",
            "paint_options": {
                "colour": "#0b0c0c",
            },
        },
        {
            "dataset": "listed-building",
            "label": "Listed buildings",
            "paint_options": {
                "colour": "#F9C744",
            },
            "type": "point",
        },
        {
            "dataset": "special-area-of-conservation",
            "label": "Special areas of conservation",
            "paint_options": {
                "colour": "#7A8705",
            },
        },
        {
            "dataset": "scheduled-monument",
            "label": "Scheduled monuments",
            "paint_options": {
                "colour": "#0F9CDA",
            },
        },
        {
            "dataset": "heritage-at-risk",
            "label": "Heritage at risk",
            "paint_options": {
                "colour": "#8D73AF",
            },
        },
        {
            "dataset": "certificate-of-immunity",
            "label": "Certificate of immunity",
            "paint_options": {
                "colour": "#D8760D",
            },
        },
        {
            "dataset": "building-preservation-notice",
            "label": "Building preservation notices",
            "paint_options": {
                "colour": "#f944c7",
            },
        },
        {
            "dataset": "ramsar",
            "label": "Ramsar",
            "paint_options": {"colour": "#7fcdff"},
        },
        {
            "dataset": "site-of-special-scientific-interest",
            "label": "Sites of special scientific interest",
            "paint_options": {
                "colour": "#308fac",
            },
        },
        {
            "dataset": "open-space",
            "label": "Open spaces",
            "paint_options": {
                "colour": "#328478",
            },
        },
    ]
    layers = sorted(
        filter(lambda layer: layer.get("active_zoom_level") is None, all_layers),
        key=lambda x: x["label"],
    )

    return templates.TemplateResponse(
        "national-map.html", {"request": request, "layers": layers}
    )
