from enum import Enum
import logging
from typing import List

from application.core.models import (
    DatasetModel,
    TypologyModel,
    OrganisationModel,
    DatasetCollectionModel,
    DatasetPublicationCountModel,
)
from application.db.models import (
    DatasetOrm,
    EntityOrm,
    OrganisationOrm,
    TypologyOrm,
    DatasetCollectionOrm,
    DatasetPublicationCountOrm,
)
from application.db.session import get_context_session

logger = logging.getLogger(__name__)


def get_datasets() -> List[DatasetModel]:
    with get_context_session() as session:
        datasets = (
            session.query(DatasetOrm)
            .filter(DatasetOrm.typology != "specification")
            .order_by(DatasetOrm.dataset)
            .all()
        )
        return [DatasetModel.from_orm(ds) for ds in datasets]


def get_dataset_query(dataset) -> DatasetModel:
    with get_context_session() as session:
        dataset = session.query(DatasetOrm).get(dataset)
        return DatasetModel.from_orm(dataset)


def get_datasets_with_data_by_typology(typology) -> List[DatasetModel]:
    from sqlalchemy import func

    with get_context_session() as session:
        query = session.query(
            DatasetOrm,
            func.count(func.distinct(EntityOrm.entity).label(("entity_count"))),
        )
        query = query.filter(
            DatasetOrm.typology == typology, DatasetOrm.dataset == EntityOrm.dataset
        )
        query = query.group_by(DatasetOrm.dataset)
        datasets = query.all()
        return [DatasetModel.from_orm(ds.DatasetOrm) for ds in datasets]


def get_typologies() -> List[TypologyModel]:
    with get_context_session() as session:
        typologies = session.query(TypologyOrm).order_by(TypologyOrm.typology).all()
        return [TypologyModel.from_orm(t) for t in typologies]


def get_local_authorities(local_authority_region) -> List[OrganisationModel]:
    with get_context_session() as session:
        organisations = (
            session.query(OrganisationOrm)
            .filter(OrganisationOrm.organisation.like(f"%{local_authority_region}%"))
            .order_by(OrganisationOrm.organisation)
            .all()
        )
        return [OrganisationModel.from_orm(o) for o in organisations]


def get_publisher_coverage(dataset) -> DatasetPublicationCountModel:
    with get_context_session() as session:
        result = session.query(DatasetPublicationCountOrm).get(dataset)
        if result is not None:
            return DatasetPublicationCountModel.from_orm(result)
        else:
            return DatasetPublicationCountModel(
                dataset_publication=dataset,
                expected_publisher_count=0,
                publisher_count=0,
            )


def get_latest_resource(dataset) -> DatasetCollectionModel:
    with get_context_session() as session:
        result = session.query(DatasetCollectionOrm).get(dataset)
        if result is not None:
            return DatasetCollectionModel.from_orm(result)
        else:
            return None


def get_dataset_names():
    with get_context_session() as session:
        return [result[0] for result in session.query(DatasetOrm.dataset).all()]


DATASET_NAMES = get_dataset_names()
DATASET_NAMES_ENUM = Enum("dataset", zip(DATASET_NAMES, DATASET_NAMES))
