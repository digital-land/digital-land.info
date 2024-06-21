import logging

from dataclasses import asdict
from typing import Optional, List, Set, Dict, Union

from fastapi import APIRouter, Depends, HTTPException, Request, Path
from pydantic import Required
from pydantic.error_wrappers import ErrorWrapper
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
from application.core.models import GeoJSON, EntityModel
from application.data_access.digital_land_queries import (
    get_datasets,
    get_local_authorities,
    get_typologies_with_entities,
    get_dataset_query,
    get_typology_names,
)
from application.data_access.entity_queries import (
    get_entity_query,
    get_entity_search,
    lookup_entity_link,
)
from application.data_access.dataset_queries import get_dataset_names

from application.search.enum import SuffixEntity
from application.search.filters import QueryFilters
from application.core.templates import templates
from application.core.utils import (
    DigitalLandJSONResponse,
    to_snake,
    entity_attribute_sort_key,
    make_links,
)
from application.exceptions import (
    DatasetValueNotFound,
    TypologyValueNotFound,
)
from application.db.session import get_session

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


def handle_gone_entity(
    request: Request, entity: int, extension: Optional[SuffixEntity]
):
    if extension:
        raise HTTPException(
            detail=f"Entity {entity} has been removed",
            status_code=410,
        )
    return templates.TemplateResponse(
        "entity-gone.html",
        {"request": request, "entity": str(entity)},
        status_code=410,
    )


def handle_moved_entity(
    entity: int, new_entity_id: int, extension: Optional[SuffixEntity]
):
    if extension:
        return RedirectResponse(f"/entity/{new_entity_id}.{extension}", status_code=301)
    return RedirectResponse(f"/entity/{new_entity_id}", status_code=301)


def prepare_geojson(e):
    if e.geojson is not None:
        geojson = e.geojson
        if geojson:
            properties = e.dict(exclude={"geojson", "geometry", "point"}, by_alias=True)
            geojson.properties = properties
        return geojson
    return None


def handle_entity_response(
    request: Request, e, extension: Optional[SuffixEntity], session: Session
):
    if extension is not None and extension.value == "json":
        return e.dict(by_alias=True, exclude={"geojson"})

    geojson = None

    if extension is not None and extension.value == "geojson":
        geojson = prepare_geojson(e)
        if geojson:
            return geojson
        else:
            raise HTTPException(
                status_code=406, detail="geojson for entity not available"
            )

    e_dict = e.dict(by_alias=True, exclude={"geojson"})
    e_dict_sorted = {
        key: e_dict[key] for key in sorted(e_dict.keys(), key=entity_attribute_sort_key)
    }

    # need to remove any dependency on facts this should be changed when fields added to postgis
    fields = None
    # get field specifications and convert to dictionary to easily access
    # fields = get_field_specifications(e_dict_sorted.keys())
    # if fields:
    #     fields = [field.dict(by_alias=True) for field in fields]
    #     fields = {field["field"]: field for field in fields}

    # get dictionary of fields which have linked datasets
    dataset_fields = get_datasets(session, datasets=e_dict_sorted.keys())
    dataset_fields = [
        dataset_field.dict(by_alias=True) for dataset_field in dataset_fields
    ]
    dataset_fields = [dataset_field["dataset"] for dataset_field in dataset_fields]

    dataset = get_dataset_query(session, e.dataset)
    organisation_entity, _, _ = get_entity_query(session, e.organisation_entity)

    entityLinkFields = [
        "article-4-direction",
        "permitted-development-rights",
        "tree-preservation-order",
    ]

    linked_entities = {}

    # for each entityLinkField, if that key exists in the entity dict, then
    # lookup the entity and add it to the linked_entities dict
    for field in entityLinkFields:
        if field in e_dict_sorted:
            linked_entity = lookup_entity_link(
                session, e_dict_sorted[field], field, e_dict_sorted["dataset"]
            )
            if linked_entity is not None:
                linked_entities[field] = linked_entity

    return templates.TemplateResponse(
        "entity.html",
        {
            "request": request,
            "row": e_dict_sorted,
            "linked_entities": linked_entities,
            "entity": e,
            "pipeline_name": e.dataset,
            "references": [],
            "breadcrumb": [],
            "schema": None,
            "typology": e.typology,
            "entity_prefix": "",
            "geojson_features": e.geojson if e.geojson is not None else None,
            "geojson": geojson.dict() if geojson else None,
            "fields": fields,
            "dataset_fields": dataset_fields,
            "dataset": dataset,
            "organisation_entity": organisation_entity,
        },
    )


def get_entity(
    request: Request,
    entity: int = Path(default=Required, description="Entity id"),
    extension: Optional[SuffixEntity] = None,
    session: Session = Depends(get_session),
):
    e, old_entity_status, new_entity_id = get_entity_query(session, entity)

    if old_entity_status == 410:
        return handle_gone_entity(request, entity, extension)
    elif old_entity_status == 301:
        return handle_moved_entity(entity, new_entity_id, extension)
    elif e is not None:
        return handle_entity_response(request, e, extension, session)
    else:
        raise HTTPException(status_code=404, detail="entity not found")


def validate_dataset(dataset: str, datasets: list):
    """
    Given a dataset and a set of datasets will check if dataset is a valid one
    if not it will raise the appropriate error. Query not included to reduce
    number of queries on the server.
    """
    if not dataset:
        return dataset

    missing_datasets = set(dataset).difference(set(datasets))
    if missing_datasets:
        raise RequestValidationError(
            errors=[
                ErrorWrapper(
                    DatasetValueNotFound(
                        f"Requested datasets do not exist: {','.join(missing_datasets)}. "
                        f"Valid dataset names: {','.join(datasets)}",
                        dataset_names=datasets,
                    ),
                    loc=("dataset"),
                )
            ]
        )
    return


def validate_typologies(typologies, typology_names):
    if not typologies:
        return typologies
    missing_typologies = set(typologies).difference(set(typology_names))
    if missing_typologies:
        raise RequestValidationError(
            errors=[
                ErrorWrapper(
                    TypologyValueNotFound(
                        f"Requested datasets do not exist: {','.join(missing_typologies)}. "
                        f"Valid dataset names: {','.join(typology_names)}",
                        dataset_names=typology_names,
                    ),
                    loc=("typology"),
                )
            ]
        )
    return


def search_entities(
    request: Request,
    query_filters: QueryFilters = Depends(),
    extension: Optional[SuffixEntity] = None,
    session: Session = Depends(get_session),
):
    # get query_filters as a dict
    query_params = asdict(query_filters)
    # TODO minimse queries by using normal queries below rather than returning the names
    # queries required for additional validations
    dataset_names = get_dataset_names(session)
    typology_names = get_typology_names(session)

    # additional validations
    validate_dataset(query_params.get("dataset", None), dataset_names)
    validate_typologies(query_params.get("typology", None), typology_names)
    # Run entity query
    data = get_entity_search(session, query_params)

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

    typologies = get_typologies_with_entities(session)
    typologies = [t.dict() for t in typologies]
    # dataset facet
    response = get_datasets(session)
    columns = ["dataset", "name", "plural", "typology", "themes", "paint_options"]
    datasets = [dataset.dict(include=set(columns)) for dataset in response]

    local_authorities = get_local_authorities(session, "local-authority")
    local_authorities = [la.dict() for la in local_authorities]

    if links.get("prev") is not None:
        prev_url = links["prev"]
    else:
        prev_url = None

    if links.get("next") is not None:
        next_url = links["next"]
    else:
        next_url = None
    # default is HTML
    has_geographies = any((e.typology == "geography" for e in data["entities"]))
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
            "has_geographies": has_geographies,
        },
    )


# Route ordering in important. Match routes with extensions first
router.add_api_route(
    ".{extension}",
    endpoint=search_entities,
    response_class=DigitalLandJSONResponse,
    tags=["Search entity"],
    summary="This endpoint searches for a subset of entities from all entities filtered by specified parameters returning the entity set in the format specified.",  # noqa: E501
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
    summary="This endpoint returns data on one specific entity matching the specified ID in the format requested.",
)
router.add_api_route(
    "/{entity}",
    endpoint=get_entity,
    response_class=HTMLResponse,
    include_in_schema=False,
)
