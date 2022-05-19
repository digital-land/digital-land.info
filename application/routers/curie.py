import logging

from fastapi import APIRouter, HTTPException
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse

from application.db.session import get_context_session

router = APIRouter()
logger = logging.getLogger(__name__)


def get_entity_redirect_by_curie(request: Request, prefix: str, reference: str):
    from application.db.models import LookupOrm

    with get_context_session() as session:
        lookup = (
            session.query(LookupOrm.entity.label("entity"))
            .filter(LookupOrm.prefix == prefix, LookupOrm.reference == reference)
            .one_or_none()
        )
    if lookup is None:
        raise HTTPException(status_code=404)
    else:
        url = request.url_for("get_entity", entity=lookup.entity)
        return RedirectResponse(url, status_code=303)


router.add_api_route(
    "/{prefix}/reference/{reference}",
    endpoint=get_entity_redirect_by_curie,
    response_class=HTMLResponse,
    include_in_schema=False,
)

router.add_api_route(
    "/{prefix}:{reference}",
    endpoint=get_entity_redirect_by_curie,
    response_class=HTMLResponse,
    include_in_schema=False,
)
