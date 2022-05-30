import logging
from datetime import date
from typing import Optional

from fastapi import APIRouter, Request
from sqlalchemy import func
from starlette.responses import HTMLResponse

from application.core.models import OrganisationModel, OrganisationsByTypeModel
from application.core.templates import templates
from application.core.utils import DigitalLandJSONResponse
from application.db.models import OrganisationOrm
from application.db.session import get_context_session
from application.search.enum import SuffixOrganisation

router = APIRouter()
logger = logging.getLogger(__name__)

display_names = {
    "development-corporation": "Development corporations",
    "government-organisation": "Government departments, agencies and public bodies",
    "local-authority-eng": "Local authorities",
    "national-park-authority": "National park authorities, including the Broads",
    "public-authority": "Public authorities",
    "regional-park-authority": "Regional park authorities",
    "transport-authority": "Transport authorities",
    "waste-authority": "Waste authorities",
}


def get_organisations(
    request: Request,
    extension: Optional[SuffixOrganisation] = None,
) -> OrganisationsByTypeModel:
    with get_context_session() as session:
        organisations_by_type = {
            o.type: []
            for o in session.query(
                func.split_part(OrganisationOrm.organisation, ":", 1).label("type")
            )
            .distinct("type")
            .all()
        }
        organisations = session.query(OrganisationOrm).all()
        for o in organisations:
            organisations_by_type[o.type()].append(OrganisationModel.from_orm(o))
    if extension == SuffixOrganisation.json:
        return OrganisationsByTypeModel(organisations=organisations_by_type)
    else:
        return templates.TemplateResponse(
            "organisation_index.html",
            {
                "request": request,
                "organisations": organisations_by_type,
                "display_names": display_names,
                "today": date.today(),
            },
        )


router.add_api_route(
    ".{extension}",
    endpoint=get_organisations,
    response_class=DigitalLandJSONResponse,
    tags=["List of organisations by type"],
)

router.add_api_route(
    "/",
    endpoint=get_organisations,
    response_class=HTMLResponse,
    include_in_schema=False,
)
