import logging

from dataclasses import asdict
from typing import Optional, List, Set, Dict, Union

from fastapi import APIRouter, Depends, HTTPException, Request, Path
from pydantic import Required
from pydantic.error_wrappers import ErrorWrapper
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session
import redis
from application.core.models import GeoJSON, EntityModel
from application.data_access.digital_land_queries import (
    get_datasets,
    get_all_datasets,
    get_local_authorities,
    get_typologies_with_entities,
    get_dataset_query,
    get_typology_names,
)
from application.data_access.entity_queries import (
    get_entity_query,
    get_entity_search,
    get_organisations,
    lookup_entity_link,
    get_linked_entities,
    fetchEntityFromReference,
)
from application.data_access.dataset_queries import get_dataset_names
from application.data_access.find_an_area_helpers import find_an_area

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
from application.db.session import get_session, get_redis, DbSession

router = APIRouter()
logger = logging.getLogger(__name__)


def _get_geojson(
    data: List[EntityModel], exclude: Optional[Set] = None
) -> Dict[str, Union[str, List[GeoJSON]]]:
    features = []
    for entity in data:
        if entity.geojson is not None:
            geojson = entity.geojson
            exclude = set(exclude) if exclude else set()
            # always remove the geospatial fields as we're only after non-gespatial prroperties
            exclude.update(["geojson", "geometry", "point"])
            properties = entity.dict(exclude=exclude, by_alias=True)
            geojson.properties = properties
            features.append(geojson)
    return {"type": "FeatureCollection", "features": features}


def _get_entity_json(
    data: List[EntityModel],
    include: Optional[Set] = None,
    exclude: Optional[List[str]] = None,
):
    entities = []
    for entity in data:
        if include is not None:
            # always return at least the entity (id)
            include.add("entity")
            e = entity.dict(include=include, by_alias=True)
        else:
            exclude = set(exclude) if exclude else set()
            exclude.add("geojson")  # Always exclude 'geojson'
            e = entity.dict(exclude=exclude, by_alias=True)
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
    geojson = e.geojson
    if geojson:
        properties = e.dict(exclude={"geojson", "geometry", "point"}, by_alias=True)
        geojson.properties = properties
    return geojson


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

    # CURIE field composed by the Prefix:Reference fields
    prefix = e_dict.get("prefix")
    reference = e_dict.get("reference")
    curie = f"{prefix}:{reference}" if prefix and reference else None

    # Add CURIE field to dict and make it first
    e_dict_sorted = {"curie": curie, **e_dict_sorted}

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
        "local-plan-boundary",
        "local-plan",
        "local-plan-event",
        "conservation-area",
        "listed-building",
    ]

    linked_entities = {}

    # for each entityLinkField, if that key exists in the entity dict, then
    # lookup the entity and add it to the linked_entities dict
    for field in entityLinkFields:
        if field in e_dict_sorted:
            linked_entity = lookup_entity_link(
                session,
                e_dict_sorted[field],
                field,
                e_dict_sorted["organisation-entity"],
            )
            if linked_entity is not None:
                linked_entities[field] = linked_entity

    # Fetch linked local plans/document/timetable
    local_plans, local_plan_boundary_geojson = fetch_linked_local_plans(
        session, e_dict_sorted
    )

    return templates.TemplateResponse(
        "entity.html",
        {
            "request": request,
            "row": e_dict_sorted,
            "local_plan_geojson": local_plan_boundary_geojson,
            "linked_entities": linked_entities,
            "local_plans": local_plans,
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
            "feedback_form_footer": True,
        },
    )


linked_datasets = {
    "local-plan-boundary": ["local-plan"],
    "local-plan": [
        "local-plan-document",
        "local-plan-timetable",
        "local-plan-boundary",
    ],
}


def fetch_linked_local_plans(session: Session, e_dict_sorted: Dict = None):
    results = {}
    local_plan_boundary_geojson = None
    dataset = e_dict_sorted["dataset"]
    reference = e_dict_sorted["reference"]
    if dataset in linked_datasets:
        linked_dataset_value = linked_datasets[dataset]
        for linked_dataset in linked_dataset_value:
            if dataset == "local-plan" and linked_dataset == "local-plan-boundary":
                if linked_dataset in e_dict_sorted:
                    local_plan_boundary_geojson = fetchEntityFromReference(
                        session, linked_dataset, e_dict_sorted[linked_dataset]
                    )
            linked_entities = get_linked_entities(
                session, linked_dataset, reference, linked_dataset=dataset
            )
            results[linked_dataset] = linked_entities

            # Handle special case for "local-plan-timetable"
            if dataset == "local-plan" and linked_dataset == "local-plan-timetable":
                for entity in linked_entities:
                    if (
                        hasattr(entity, "local_plan_event")
                        and entity.local_plan_event
                        and not entity.local_plan_event.startswith("estimated")
                    ):
                        entity.local_plan_event = fetchEntityFromReference(
                            session, "local-plan-event", entity.local_plan_event
                        )
                    else:
                        entity.local_plan_event = None

    return results, local_plan_boundary_geojson


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
    redis: redis.Redis = Depends(get_redis),
):
    # Determine if the URL path includes an extension
    if "." in request.url.path:  # check if extension if in path parameter
        extension = extension
    else:
        if request.query_params.get(
            "extension"
        ):  # check if extension if in query parameter
            extension = None

    # get query_filters as a dict
    query_params = asdict(query_filters)
    # TODO minimse queries by using normal queries below rather than returning the names
    # queries required for additional validations
    dataset_names = get_dataset_names(session)
    typology_names = get_typology_names(session)

    # Find an area - Postcode / UPRN search
    query = query_params.get("q")
    if not query or not query.strip():
        find_an_area_result = None
    else:
        find_an_area_result = find_an_area(query)

    find_an_area_latitude = None
    find_an_area_longitude = None

    if find_an_area_result and find_an_area_result.get("result", {}):
        result_data = find_an_area_result.get("result", {})
        find_an_area_latitude = result_data.get("LAT")
        find_an_area_longitude = result_data.get("LNG")

    if find_an_area_latitude and find_an_area_longitude:
        query_params.update(
            {
                "latitude": find_an_area_latitude,
                "longitude": find_an_area_longitude,
            }
        )

    # additional validations
    validate_dataset(query_params.get("dataset", None), dataset_names)
    validate_typologies(query_params.get("typology", None), typology_names)
    # Run entity query
    data = get_entity_search(session, query_params, extension)
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
        elif params.get("exclude_field") is not None:
            exclude_fields = set(
                [
                    to_snake(field.strip())
                    for field in ",".join(params.get("exclude_field")).split(",")
                ]
            )
            entities = _get_entity_json(data["entities"], exclude=exclude_fields)
        else:
            entities = _get_entity_json(data["entities"])
        return {"entities": entities, "links": links, "count": data["count"]}

    if extension is not None and extension.value == "geojson":
        if params.get("exclude_field") is not None:
            exclude_fields = set(
                [
                    to_snake(field.strip())
                    for field in ",".join(params.get("exclude_field")).split(",")
                ]
            )
            geojson = _get_geojson(data["entities"], exclude=exclude_fields)
        else:
            geojson = _get_geojson(data["entities"])
        geojson["links"] = links
        return geojson

    db_session = DbSession(session=session, redis=redis)
    typologies = get_typologies_with_entities(db_session)
    typologies = [t.dict() for t in typologies]
    # dataset facet
    response = get_all_datasets(db_session)
    columns = ["dataset", "name", "plural", "typology", "themes", "paint_options"]
    datasets = [dataset.dict(include=set(columns)) for dataset in response]

    local_authorities = get_local_authorities(session, "local-authority")
    local_authorities = [la.dict() for la in local_authorities]

    organisations = get_organisations(db_session)
    columns = ["entity", "organisation_entity", "name"]
    organisations_list = [
        organisation.dict(include=set(columns)) for organisation in organisations
    ]

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
    # add dataset name
    dataset_name_lookup = {d["dataset"]: d["name"] for d in datasets}
    for entity in data["entities"]:
        ref_name = entity.dataset
        if ref_name and ref_name in dataset_name_lookup:
            entity.dataset_name = dataset_name_lookup[ref_name]
        else:
            entity.dataset_name = ref_name
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
            "organisations": organisations_list,
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
            "find_an_area_result": find_an_area_result,
            "feedback_form_footer": True,
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
