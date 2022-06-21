import logging
import json

from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from application.data_access.entity_queries import get_entity_query
from application.data_access.fact_queries import get_entity_facts_query

from application.search.enum import SuffixEntity
from application.core.templates import templates
from application.core.utils import (
    DigitalLandJSONResponse,
    entity_attribute_sort_key,
)

router = APIRouter()
logger = logging.getLogger(__name__)


def _convert_resources_to_dict(fact):
    fact["resource-history"] = json.loads(fact["resource-history"])
    return fact


def get_entity_facts(
    request: Request, entity: int, extension: Optional[SuffixEntity] = None
):

    e, old_entity_status, new_entity_id = get_entity_query(entity)

    if old_entity_status == 410:
        return templates.TemplateResponse(
            "entity-gone.html",
            {
                "request": request,
                "entity": str(entity),
            },
        )
    elif old_entity_status == 301:
        if extension:
            return RedirectResponse(
                f"/fact/{new_entity_id}.{extension}", status_code=301
            )
        else:
            return RedirectResponse(f"/fact/{new_entity_id}", status_code=301)
    elif e is not None:
        facts = get_entity_facts_query(e)
        if extension is not None and extension.value == "json":
            return facts

        e_dict = e.dict(by_alias=True, exclude={"geojson"})
        e_dict_sorted = {
            key: e_dict[key]
            for key in sorted(e_dict.keys(), key=entity_attribute_sort_key)
        }

        facts_dicts = [fact.dict(by_alias=True) for fact in facts]
        facts_dicts = [_convert_resources_to_dict(fact) for fact in facts_dicts]

        return templates.TemplateResponse(
            "entity-facts.html",
            {
                "request": request,
                "facts": facts_dicts,
                "row": e_dict_sorted,
            },
        )
    else:
        raise HTTPException(status_code=404, detail="entity not found")


router.add_api_route(
    "/{entity}.{extension}",
    get_entity_facts,
    response_class=DigitalLandJSONResponse,
    tags=["Get facts for a single entity"],
)
router.add_api_route(
    "/{entity}",
    endpoint=get_entity_facts,
    response_class=HTMLResponse,
    include_in_schema=False,
)
