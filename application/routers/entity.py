import logging

from dataclasses import asdict
from typing import Optional, List, Set, Dict, Union

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from application.core.models import GeoJSON, EntityModel
from application.data_access.datasette_digital_land_queries import (
    get_field_specifications,
)
from application.data_access.digital_land_queries import (
    get_datasets,
    get_local_authorities,
    get_typologies,
)
from application.data_access.entity_queries import get_entity_query, get_entity_search

from application.search.enum import SuffixEntity
from application.search.filters import QueryFilters
from application.core.templates import templates
from application.core.utils import (
    DigitalLandJSONResponse,
    to_snake,
    entity_attribute_sort_key,
    make_links,
)

router = APIRouter()
logger = logging.getLogger(__name__)


def _get_geojson(data: List[EntityModel]) -> Dict[str, Union[str, List[GeoJSON]]]:
    features = []
    for entity in data:
        if entity.geojson is not None:
            geojson = entity.geojson
            properties = entity.dict(
                exclude={"geojson", "geometry", "point"}, by_alias=True
            )
            geojson.properties = properties
            features.append(geojson)
    return {"type": "FeatureCollection", "features": features}


def _get_entity_json(data: List[EntityModel], include: Optional[Set] = None):
    entities = []
    for entity in data:
        if include is not None:
            # always return at least the entity (id)
            include.add("entity")
            e = entity.dict(include=include, by_alias=True)
        else:
            e = entity.dict(exclude={"geojson"}, by_alias=True)
        entities.append(e)
    return entities


def get_entity(request: Request, entity: int, extension: Optional[SuffixEntity] = None):

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
                f"/entity/{new_entity_id}.{extension}", status_code=301
            )
        else:
            return RedirectResponse(f"/entity/{new_entity_id}", status_code=301)
    elif e is not None:

        if extension is not None and extension.value == "json":
            return e.dict(by_alias=True, exclude={"geojson"})

        if e.geojson is not None:
            geojson = e.geojson
            properties = e.dict(exclude={"geojson", "geometry", "point"}, by_alias=True)
            geojson.properties = properties
        else:
            geojson = None

        if extension is not None and extension.value == "geojson":
            if geojson is not None:
                return geojson
            else:
                raise HTTPException(
                    status_code=406, detail="geojson for entity not available"
                )

        e_dict = e.dict(by_alias=True, exclude={"geojson"})
        e_dict_sorted = {
            key: e_dict[key]
            for key in sorted(e_dict.keys(), key=entity_attribute_sort_key)
        }

        if geojson is not None:
            geojson_dict = dict(geojson)
        else:
            geojson_dict = None

        # get field specifications and convert to dictionary to easily access
        fields = get_field_specifications(e_dict_sorted.keys())
        if fields:
            fields = [field.dict(by_alias=True) for field in fields]
            fields = {field["field"]: field for field in fields}

        # get dictionary of fields which have linked datasets
        dataset_fields = get_datasets(datasets=fields.keys())
        dataset_fields = [
            dataset_field.dict(by_alias=True) for dataset_field in dataset_fields
        ]
        dataset_fields = [dataset_field["dataset"] for dataset_field in dataset_fields]

        return templates.TemplateResponse(
            "entity.html",
            {
                "request": request,
                "row": e_dict_sorted,
                "entity": e_dict_sorted,
                "pipeline_name": e.dataset,
                "references": [],
                "breadcrumb": [],
                "schema": None,
                "typology": e.typology,
                "entity_prefix": "",
                "geojson_features": e.geojson if e.geojson is not None else None,
                "geojson": geojson_dict,
                "fields": fields,
                "dataset_fields": dataset_fields,
            },
        )
    else:
        raise HTTPException(status_code=404, detail="entity not found")


def search_entities(
    request: Request,
    query_filters: QueryFilters = Depends(),
    extension: Optional[SuffixEntity] = None,
):
    query_params = asdict(query_filters)
    data = get_entity_search(query_params)

    # the query does some normalisation to remove empty
    # params and they get returned from search
    params = data["params"]
    scheme = request.url.scheme
    netloc = request.url.netloc
    path = request.url.path
    query = request.url.query
    links = make_links(scheme, netloc, path, query, data)

    if extension is not None and extension.value == "json":

        if params.get("field") is not None:
            include = set([to_snake(field) for field in params.get("field")])
            entities = _get_entity_json(data["entities"], include=include)
        else:
            entities = _get_entity_json(data["entities"])
        return {"entities": entities, "links": links, "count": data["count"]}

    if extension is not None and extension.value == "geojson":
        geojson = _get_geojson(data["entities"])
        geojson["links"] = links
        return geojson

    # typology facet
    typologies = get_typologies()
    typologies = [t.dict() for t in typologies]
    # dataset facet
    response = get_datasets()
    columns = ["dataset", "name", "plural", "typology", "themes"]
    datasets = [dataset.dict(include=set(columns)) for dataset in response]

    local_authorities = get_local_authorities("local-authority-eng")
    local_authorities = [la.dict() for la in local_authorities]

    if links.get("prev") is not None:
        prev_url = links["prev"]
    else:
        prev_url = None

    if links.get("next") is not None:
        next_url = links["next"]
    else:
        next_url = None
    logging.error(params.items())
    logging.error(
        [
            filter_name
            for filter_name, values in params.items()
            if filter_name != "limit" and values is not None
        ]
    )
    # default is HTML
    return templates.TemplateResponse(
        "search.html",
        {
            "request": request,
            "count": data["count"],
            "limit": params["limit"],
            "data": data["entities"],
            "datasets": datasets,
            "local_authorities": local_authorities,
            "typologies": typologies,
            "query": {"params": params},
            "active_filters": [
                filter_name
                for filter_name, values in params.items()
                if filter_name != "limit" and values is not None
            ],
            "url_query_params": {
                "str": ("&").join(
                    [
                        "{}={}".format(param[0], param[1])
                        for param in request.query_params._list
                    ]
                ),
                "list": request.query_params._list,
            },
            "next_url": next_url,
            "prev_url": prev_url,
        },
    )


# Route ordering in important. Match routes with extensions first
router.add_api_route(
    ".{extension}",
    endpoint=search_entities,
    response_class=DigitalLandJSONResponse,
    tags=["Search entity"],
)
router.add_api_route(
    "/",
    endpoint=search_entities,
    responses={
        200: {
            "content": {
                "application/x-qgis-project": {},
                "application/geo+json": {},
                "text/json": {},
            },
            "description": "List of entities in one of a number of different formats.",
        }
    },
    response_class=HTMLResponse,
    include_in_schema=False,
)

router.add_api_route(
    "/{entity}.{extension}",
    get_entity,
    response_class=DigitalLandJSONResponse,
    tags=["Get entity"],
)
router.add_api_route(
    "/{entity}",
    endpoint=get_entity,
    response_class=HTMLResponse,
    include_in_schema=False,
)
