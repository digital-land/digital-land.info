import logging

from fastapi import APIRouter, HTTPException, Depends
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from application.db.models import LookupOrm, EntityOrm
from application.db.session import get_session

router = APIRouter()
logger = logging.getLogger(__name__)


def get_entity_redirect_by_curie(
    request: Request,
    prefix: str,
    reference: str,
    session: Session = Depends(get_session),
):
    lookup = (
        session.query(LookupOrm.entity.label("entity"))
        .filter(LookupOrm.prefix == prefix, LookupOrm.reference == reference)
        .first()
    )
    if lookup is None:
        lookup = (
            session.query(EntityOrm.entity.label("entity"))
            .filter(EntityOrm.prefix == prefix, EntityOrm.reference == reference)
            .first()
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
