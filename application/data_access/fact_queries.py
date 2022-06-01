from typing import List

from application.core.models import FactModel
from application.db.models import FactOrm
from application.db.session import get_context_session


def get_entity_facts(entity: int) -> List[FactModel]:
    with get_context_session() as session:
        facts = session.query(FactOrm).filter(FactOrm.entity == entity).all()
        return [FactModel.from_orm(f) for f in facts]
