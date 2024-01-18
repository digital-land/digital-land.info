from sqlalchemy.orm import Session

from application.db.models import DatasetOrm


def get_dataset_names(session: Session):
    dataset_names = [
        result[0]
        for result in session.query(DatasetOrm.dataset)
        .where(DatasetOrm.typology != "specification")
        .all()
    ]
    return dataset_names
