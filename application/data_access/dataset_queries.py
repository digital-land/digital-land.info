from application.db.models import DatasetOrm
from application.db.session import DbSession, redis_cache


@redis_cache("dataset-names", model_class=None, ttl_seconds=6 * 60 * 60)
def get_dataset_names(db_session: DbSession):
    dataset_names = [
        result[0]
        for result in db_session.session.query(DatasetOrm.dataset)
        .where(DatasetOrm.typology != "specification")
        .all()
    ]
    return dataset_names
