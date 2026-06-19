import logging

from sqlalchemy import func
from sqlalchemy.orm import Session

from application.core.models import TaskModel
from application.db.models import TaskOrm

logger = logging.getLogger(__name__)


def get_task_search(session: Session, params: dict) -> dict:
    params = {k: v for k, v in params.items() if v is not None and v != [] and v != ""}

    query = session.query(TaskOrm)

    if params.get("dataset"):
        query = query.filter(TaskOrm.dataset.in_(params["dataset"]))
    if params.get("organisation"):
        query = query.filter(TaskOrm.organisation.in_(params["organisation"]))
    if params.get("severity"):
        query = query.filter(TaskOrm.severity.in_(params["severity"]))
    if params.get("responsibility"):
        query = query.filter(TaskOrm.responsibility.in_(params["responsibility"]))
    if params.get("task_source"):
        query = query.filter(TaskOrm.task_source.in_(params["task_source"]))

    count_subquery = query.with_entities(TaskOrm.reference).subquery()
    count = session.query(func.count()).select_from(count_subquery).scalar()

    query = query.order_by(TaskOrm.reference)
    query = query.limit(params.get("limit", 10))
    if params.get("offset"):
        query = query.offset(params["offset"])

    tasks = [TaskModel.from_orm(row) for row in query.all()]
    return {"params": params, "count": count, "tasks": tasks}
