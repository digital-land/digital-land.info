import logging

from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from application.core.utils import (
    DigitalLandJSONResponse,
)
from application.search.enum import SuffixEntity
from application.data_access.curie_queries import (
    get_lookup_by_curie,
    get_entity_by_curie,
)
from application.db.session import get_session

router = APIRouter()
logger = logging.getLogger(__name__)


def get_entity_redirect_by_curie(
    request: Request,
    prefix: str,
    reference: str,
    session: Session = Depends(get_session),
    extension: Optional[SuffixEntity] = None,
):
    lookup = get_lookup_by_curie(session, prefix, reference)
    if len(lookup) == 0:
        lookup = get_entity_by_curie(session, prefix, reference)

    if len(lookup) == 0:
        raise HTTPException(status_code=404)
    else:
        if len(lookup) > 1:
            # If there are more than 1 entities with the same
            # CURIE (prefix:reference) as a temporary work-around
            # we redirect the users to the search page
            # displaying all the duplicates
            url = f"{request.url_for('search_entities')}?curie={prefix}:{reference}"
        elif extension:
            url = request.url_for(
                "get_entity", entity=lookup[0], extension=extension.value
            )
        else:
            # If the entity is unique there should be only 1 ID
            # being returned from the query, which we can access
            # at index 0
            url = request.url_for("get_entity", entity=lookup[0])
        return RedirectResponse(url, status_code=303)


router.add_api_route(
    "/{prefix}/reference/{reference}.{extension}",
    endpoint=get_entity_redirect_by_curie,
    response_class=HTMLResponse,
    include_in_schema=False,
)

router.add_api_route(
    "/{prefix}/reference/{reference}",
    endpoint=get_entity_redirect_by_curie,
    response_class=HTMLResponse,
    include_in_schema=False,
)


router.add_api_route(
    "/{prefix}:{reference}.{extension}",
    endpoint=get_entity_redirect_by_curie,
    response_class=DigitalLandJSONResponse,
    include_in_schema=False,
)

router.add_api_route(
    "/{prefix}:{reference}",
    endpoint=get_entity_redirect_by_curie,
    response_class=HTMLResponse,
    include_in_schema=False,
)
