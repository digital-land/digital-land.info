import logging
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func
from application.db.session import session_cache

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

logger = logging.getLogger(__name__)


def get_datasets(session: Session, datasets=None) -> List[DatasetModel]:
    query = (
        session.query(DatasetOrm)
        .filter(DatasetOrm.typology != "specification")
        .order_by(DatasetOrm.dataset)
    )

    if datasets:
        query = query.filter(DatasetOrm.dataset.in_(datasets))

    datasets = query.all()
    return [DatasetModel.from_orm(ds) for ds in datasets]


@session_cache("datasets")
def get_all_datasets(session: Session) -> List[DatasetModel]:
    return get_datasets(session)


def get_dataset_query(session: Session, dataset) -> DatasetModel:
    dataset = session.query(DatasetOrm).get(dataset)
    if dataset is not None:
        return DatasetModel.from_orm(dataset)
    return None


def get_datasets_with_data_by_typology(
    session: Session, typology
) -> List[DatasetModel]:
    query = session.query(DatasetOrm).join(
        EntityOrm, DatasetOrm.dataset == EntityOrm.dataset
    )
    query = query.filter(DatasetOrm.typology == typology)
    query = query.group_by(DatasetOrm.dataset)
    query = query.having(func.count(EntityOrm.entity) > 0)
    datasets = query.all()
    return [DatasetModel.from_orm(ds) for ds in datasets]


def get_typologies(session: Session) -> List[TypologyModel]:
    typologies = session.query(TypologyOrm).order_by(TypologyOrm.typology).all()
    return [TypologyModel.from_orm(t) for t in typologies]


# returns all typologies with at least one dataset that falls under that typology
@session_cache("typologies+entities")
def get_typologies_with_entities(session: Session) -> List[TypologyModel]:
    typologiesNamesRes = session.query(EntityOrm.typology).distinct().all()
    if len(typologiesNamesRes) == 0:
        return []

    typologiesNamesDict = [
        typologiesNamesRes[i][0] for i in range(len(typologiesNamesRes))
    ]

    typologies = (
        session.query(TypologyOrm)
        .filter(TypologyOrm.typology.in_(typologiesNamesDict))
        .order_by(TypologyOrm.typology)
        .all()
    )
    return [TypologyModel.from_orm(t) for t in typologies]


def get_typology_names(session: Session):
    typology_names = [result[0] for result in session.query(TypologyOrm.typology).all()]
    return typology_names


def get_local_authorities(
    session: Session, local_authority_region
) -> List[OrganisationModel]:
    organisations = (
        session.query(OrganisationOrm)
        .filter(OrganisationOrm.organisation.like(f"%{local_authority_region}%"))
        .order_by(OrganisationOrm.organisation)
        .all()
    )
    return [OrganisationModel.from_orm(o) for o in organisations]


def get_publisher_coverage(session: Session, dataset) -> DatasetPublicationCountModel:
    result = session.query(DatasetPublicationCountOrm).get(dataset)
    if result is not None:
        return DatasetPublicationCountModel.from_orm(result)
    else:
        return DatasetPublicationCountModel(
            dataset_publication=dataset,
            expected_publisher_count=0,
            publisher_count=0,
        )


def get_latest_resource(session: Session, dataset) -> DatasetCollectionModel:
    result = session.query(DatasetCollectionOrm).get(dataset)
    if result is not None:
        return DatasetCollectionModel.from_orm(result)
    else:
        return None
