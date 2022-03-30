from collections import defaultdict
from csv import DictWriter
from dataclasses import asdict
from io import StringIO
import logging
from typing import DefaultDict, Optional, List

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, Response

from application.core.models import GeoJSONFeatureCollection, EntityModel
from application.data_access.digital_land_queries import (
    get_datasets,
    get_local_authorities,
    get_typologies,
)
from application.data_access.entity_queries import (
    get_entity_query,
    get_entity_search,
)

from application.search.enum import Suffix
from application.search.filters import QueryFilters
from application.core.templates import templates
from application.core.utils import DigitalLandJSONResponse

router = APIRouter()
logger = logging.getLogger(__name__)


def _get_geojson(data: List[EntityModel]) -> GeoJSONFeatureCollection:
    results = [item.geojson for item in data]
    return {"type": "FeatureCollection", "features": results}


def get_entity(request: Request, entity: int, extension: Optional[Suffix] = None):

    e = get_entity_query(entity)
    if e is not None:

        if _is_matching_extension(extension, Suffix.json):
            return e

        if _is_matching_extension(extension, Suffix.geojson):
            return e.geojson

        if _is_matching_extension(extension, Suffix.csv):
            payload = flatten_payload(e)
            return to_csv(payload)

        return templates.TemplateResponse(
            "entity.html",
            {
                "request": request,
                "row": e.dict(by_alias=True, exclude={"geojson"}),
                "entity": e.dict(by_alias=True, exclude={"geojson"}),
                "pipeline_name": e.dataset,
                "references": [],
                "breadcrumb": [],
                "schema": None,
                "typology": e.typology,
                "entity_prefix": "",
                "geojson_features": e.geojson if e.geojson is not None else None,
            },
        )
    else:
        raise HTTPException(status_code=404, detail="entity not found")


def make_pagination_query_str(query_params, limit, offset=0):
    params = query_params.items()
    if not params:
        return f"?limit={limit}&offset={limit+offset}"
    url = "?" + "&".join(
        [
            "{}={}".format(param[0], param[1])
            for param in params
            if param[1] and param[0] != "offset"
        ]
    )
    if "limit" not in [p[0] for p in params]:
        url = f"{url}&limit={limit}"
    if offset != 0:
        return f"{url}&offset={offset}"
    else:
        return url


def make_links(request, data):
    count = data["count"]
    limit = data["params"]["limit"]
    query_str = make_pagination_query_str(request.query_params, limit)

    pagination_links = {
        "first": f"{request.url.scheme}://{request.url.netloc}{request.url.path}{query_str}"
    }

    offset = data["params"].get("offset", 0)
    limit = data["params"].get("limit")

    next_offset = offset + limit
    if next_offset < count:
        query_str = make_pagination_query_str(request.query_params, limit, next_offset)
        next_url = (
            f"{request.url.scheme}://{request.url.netloc}{request.url.path}{query_str}"
        )
        pagination_links["next"] = next_url

    if offset != 0:
        prev_offset = offset - limit
        query_str = make_pagination_query_str(request.query_params, limit, prev_offset)
        prev_url = (
            f"{request.url.scheme}://{request.url.netloc}{request.url.path}{query_str}"
        )
        pagination_links["prev"] = prev_url

    count = data["count"]
    last_offset = count - limit
    if last_offset < count:
        query_str = make_pagination_query_str(request.query_params, limit, last_offset)
        last_url = (
            f"{request.url.scheme}://{request.url.netloc}{request.url.path}{query_str}"
        )
        pagination_links["last"] = last_url

    return pagination_links


def search_entities(
    request: Request,
    query_filters: QueryFilters = Depends(),
    extension: Optional[Suffix] = None,
):
    query_params = asdict(query_filters)
    data = get_entity_search(
        query_params,
        is_unpaginated_iterator=_is_matching_extension(extension, Suffix.csv),
    )

    # the query does some normalisation to remove empty
    # params and they get returned from search
    params = data["params"]

    if _is_matching_extension(extension, Suffix.json):
        links = make_links(request, data)
        return {"entities": data["entities"], "links": links, "count": data["count"]}

    if _is_matching_extension(extension, Suffix.geojson):
        geojson = _get_geojson(data["entities"])
        links = make_links(request, data)
        geojson["links"] = links
        return geojson

    if _is_matching_extension(extension, Suffix.csv):
        payload = flatten_payload(data["entities"])
        return to_csv(payload, data["keys"])

    # typology facet
    typologies = get_typologies()
    typologies = [t.dict() for t in typologies]
    # dataset facet
    response = get_datasets()
    columns = ["dataset", "name", "plural", "typology", "themes"]
    datasets = [dataset.dict(include=set(columns)) for dataset in response]

    local_authorities = get_local_authorities("local-authority-eng")
    local_authorities = [la.dict() for la in local_authorities]

    if params.get("offset") is not None:
        offset = params["offset"] + params["limit"]
    else:
        offset = params["limit"]
    next_url = make_pagination_query_str(request.query_params, params["limit"], offset)

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
        },
    )


def _is_matching_extension(extension: Optional[Suffix], match: Suffix):
    return extension is not None and extension.value == match


def flatten_payload(data: List[EntityModel]) -> List[DefaultDict[str, str]]:
    """
    Flatten_payload so that `json` fields are top level attributes.

    This is an expensive operation, as we need the structure to be consistent for serialization,
    so we use a `defaultdict` to provide that consistency at attribute access time

    :param data:
    :type data: List[EntityModel]
    :rtype: List[dict]
    """
    for entity_model in data:
        entity_dict = defaultdict(str)
        entity_dict.update(entity_model.dict())
        entity_dict.update(entity_dict.pop("json_", {}) or {})
        yield entity_dict


def to_csv(payload: List[DefaultDict[str, str]], keys: List[str]) -> Response:
    with StringIO("") as stream:
        csv_payload_stream = DictWriter(stream, fieldnames=keys)
        csv_payload_stream.writeheader()
        for item in payload:
            csv_payload_stream.writerow(item)
        payload_body = stream.getvalue()
    return Response(
        content=payload_body,
        media_type="application/csv",
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
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": {},
                "application/zip": {},
                "application/x-qgis-project": {},
                "application/geo+json": {},
                "text/json": {},
                "text/csv": {},
                "text/turtle": {},
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
