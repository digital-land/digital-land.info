import logging
from dataclasses import asdict

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from application.data_access.task_queries import get_task_search
from application.search.filters import TaskQueryFilters
from application.core.utils import DigitalLandJSONResponse, make_links
from application.db.session import get_session

router = APIRouter()
logger = logging.getLogger(__name__)


def list_tasks(
    request: Request,
    query_filters: TaskQueryFilters = Depends(),
    session: Session = Depends(get_session),
):
    params = asdict(query_filters)
    data = get_task_search(session, params)

    links = make_links(
        request.url.scheme,
        request.url.netloc,
        request.url.path,
        request.url.query,
        data,
    )

    tasks = [t.dict(by_alias=True) for t in data["tasks"]]
    return {"tasks": tasks, "count": data["count"], "links": links}


router.add_api_route(
    ".{extension}",
    endpoint=list_tasks,
    methods=["GET"],
    response_class=DigitalLandJSONResponse,
    tags=["List tasks"],
    summary="List tasks, optionally filtered by dataset, organisation, severity, responsibility or task-source.",
    include_in_schema=False,
)

router.add_api_route(
    "/",
    endpoint=list_tasks,
    methods=["GET"],
    response_class=DigitalLandJSONResponse,
    include_in_schema=False,
)
