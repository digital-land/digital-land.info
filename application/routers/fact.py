import logging
import json

from typing import Optional
from dataclasses import asdict
from urllib.parse import urlencode
from sqlalchemy.orm import Session

from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse
from application.search.filters import (
    FactPathParams,
    FactDatasetQueryFilters,
    FactQueryFilters,
)

from application.db.session import get_session
from application.data_access.entity_queries import get_entity_query
from application.data_access.fact_queries import (
    get_fact_query,
    get_search_facts_query,
    get_dataset_fields,
)

from application.search.enum import SuffixEntity
from application.core.templates import templates
from application.core.utils import (
    DigitalLandJSONResponse,
)

router = APIRouter()
logger = logging.getLogger(__name__)


def _convert_resources_to_dict(fact):
    fact["resources"] = json.loads(fact["resources"])
    return fact


def _convert_model_to_dict(models):
    if models is None:
        return []
    if isinstance(models, list):
        if len(models) > 0:
            return [m.dict(by_alias=True) for m in models]
        else:
            return models
    else:
        return models.dict(by_alias=True)


def get_fact(
    request: Request,
    path_params: FactPathParams = Depends(),
    query_filters: FactDatasetQueryFilters = Depends(),
    extension: Optional[SuffixEntity] = None,
):
    query_params = asdict(query_filters)
    path_params = asdict(path_params)
    fact = get_fact_query(path_params["fact"], query_params["dataset"])

    if fact is not None:
        if extension is not None and extension.value == "json":
            return fact.dict(by_alias=True, exclude={"geojson"})

        if extension is not None and extension.value == "geojson":
            if fact.geojson is not None:
                geojson = fact.geojson
                properties = fact.dict(
                    exclude={"geojson", "geometry", "point"}, by_alias=True
                )
                geojson.properties = properties
                return geojson
            else:
                raise HTTPException(
                    status_code=406, detail="geojson for entity not available"
                )

        fact_dict = fact.dict(by_alias=True, exclude={"geojson"})
        fact_dict = _convert_resources_to_dict(fact_dict)

        return templates.TemplateResponse(
            "fact.html",
            {
                "request": request,
                "fact": fact_dict,
                "pipeline_name": query_params["dataset"],
                "references": [],
                "breadcrumb": [],
                "schema": None,
                "entity_prefix": "",
            },
        )
    else:
        raise HTTPException(status_code=404, detail="fact not found")


def search_facts(
    request: Request,
    query_filters: FactQueryFilters = Depends(),
    extension: Optional[SuffixEntity] = None,
    session: Session = Depends(get_session),
):
    query_params = asdict(query_filters)

    facts = get_search_facts_query(query_params)

    if facts is not None:
        if extension is not None and extension.value == "json":
            return facts

        facts_dicts = _convert_model_to_dict(facts)

        dataset_fields = get_dataset_fields(
            dataset=query_params["dataset"], entity=query_params["entity"]
        )

        dataset_fields_dicts = _convert_model_to_dict(dataset_fields)

        if dataset_fields_dicts is None or len(dataset_fields_dicts) == 0:
            logging.warning("dataset fields cannot be retrieved")

        dataset_fields_list = [field["field"] for field in dataset_fields_dicts]

        if query_params.get("field"):
            for field in query_params["field"]:
                if field not in dataset_fields_list:
                    dataset_fields_list.append(field)
        if len(facts) > 0:
            entity_name = facts_dicts[0]["entity-name"]
            entity_prefix = facts_dicts[0]["entity-prefix"]
            entity_reference = facts_dicts[0]["entity-reference"]
        else:
            e, old_entity_status, new_entity_id = get_entity_query(
                session, query_params["entity"]
            )
            if e:
                entity_name = e.name
                entity_prefix = e.prefix
                entity_reference = e.reference
            else:
                entity_name = None
                entity_prefix = None
                entity_reference = None

        return templates.TemplateResponse(
            "fact-search.html",
            {
                "request": request,
                "facts": facts_dicts,
                "dataset_fields": dataset_fields_list,
                "query_params": query_params,
                "query_params_str": urlencode(
                    {k: v for k, v in query_params.items()}, doseq=True
                ),
                "entity_name": entity_name,
                "entity_prefix": entity_prefix,
                "entity_reference": entity_reference,
            },
        )
    else:
        logging.warning("facts cannot be retrieved")

        if extension is not None and extension.value == "json":
            return []
        else:
            raise HTTPException(status_code=404, detail="fact not found")


router.add_api_route(
    ".{extension}",
    endpoint=search_facts,
    response_class=DigitalLandJSONResponse,
    tags=["Search entity"],
    include_in_schema=False,
)
router.add_api_route(
    "/",
    endpoint=search_facts,
    responses={
        200: {
            "content": {
                "application/x-qgis-project": {},
                "application/geo+json": {},
                "text/json": {},
            },
            "description": "List of facts in one of a number of different formats.",
        }
    },
    response_class=HTMLResponse,
    include_in_schema=False,
)

router.add_api_route(
    "/{fact}.{extension}",
    get_fact,
    response_class=DigitalLandJSONResponse,
    tags=["Get a single fact"],
    include_in_schema=False,
)
router.add_api_route(
    "/{fact}",
    endpoint=get_fact,
    response_class=HTMLResponse,
    include_in_schema=False,
)
