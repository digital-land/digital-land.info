import logging
from datetime import date
from typing import Optional

from fastapi import APIRouter, Request, Depends
from sqlalchemy import func
from starlette.responses import HTMLResponse
from sqlalchemy.orm import Session

from application.core.models import OrganisationModel, OrganisationsByTypeModel
from application.core.templates import templates
from application.core.utils import DigitalLandJSONResponse
from application.db.models import OrganisationOrm
from application.db.session import get_session
from application.search.enum import SuffixOrganisation
from application.settings import get_settings, Settings

router = APIRouter()
logger = logging.getLogger(__name__)

# TODO check we still need these display names
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


# TODO move data access to separate functions in data access folder
def get_organisations(
    request: Request,
    extension: Optional[SuffixOrganisation] = None,
    settings: Settings = Depends(get_settings),
    session: Session = Depends(get_session),
) -> OrganisationsByTypeModel:
    data_file_url = settings.DATA_FILE_URL
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
                "data_file_url": data_file_url,
                "feedback_form_footer": True,
            },
        )


router.add_api_route(
    ".{extension}",
    endpoint=get_organisations,
    response_class=DigitalLandJSONResponse,
    tags=["List of organisations by type"],
    include_in_schema=False,
)

router.add_api_route(
    "/",
    endpoint=get_organisations,
    response_class=HTMLResponse,
    include_in_schema=False,
)
