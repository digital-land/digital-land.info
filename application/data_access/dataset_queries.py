from application.db.models import DatasetOrm
from application.db.session import get_context_session


def get_dataset_names():
    with get_context_session() as session:
        dataset_names = [
            result[0]
            for result in session.query(DatasetOrm.dataset)
            .where(DatasetOrm.typology != "specification")
            .all()
        ]
    return dataset_names
