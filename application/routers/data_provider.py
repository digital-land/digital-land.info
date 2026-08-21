import logging

from fastapi import APIRouter, Request, Depends, HTTPException, Path
from starlette.responses import HTMLResponse
from sqlalchemy.orm import Session

from application.core.templates import templates
from application.data_access.digital_land_queries import (
    get_dataset_query,
    get_providers_for_dataset,
)
from application.db.session import get_session

router = APIRouter()
logger = logging.getLogger(__name__)


def get_providers(
    request: Request,
    dataset: str = Path(description="Specify which dataset"),
    session: Session = Depends(get_session),
):
    _dataset = get_dataset_query(session, dataset)
    if _dataset is None:
        raise HTTPException(
            status_code=404,
            detail=f"dataset '{dataset}' not found for data providers page",
        )

    providers = get_providers_for_dataset(session, dataset)
    authoritative_providers = [p for p in providers if p.quality == "authoritative"]
    alternative_providers = [p for p in providers if p.quality != "authoritative"]

    return templates.TemplateResponse(
        request,
        "data_provider_index.html",
        {
            "dataset": _dataset,
            "authoritative_providers": authoritative_providers,
            "alternative_providers": alternative_providers,
            "feedback_form_footer": True,
        },
    )


router.add_api_route(
    "/{dataset}",
    endpoint=get_providers,
    response_class=HTMLResponse,
    include_in_schema=False,
)
