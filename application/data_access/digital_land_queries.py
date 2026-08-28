import logging
import yaml
from typing import List
from sqlalchemy import func
from sqlalchemy.orm import Session

from application.core.models import (
    DatasetModel,
    TypologyModel,
    OrganisationModel,
    DatasetCollectionModel,
    ProviderModel,
)
from application.db.session import redis_cache, DbSession
from application.core.utils import log_slow_execution
from application.db.models import (
    DatasetOrm,
    EntityOrm,
    OrganisationOrm,
    TypologyOrm,
    DatasetCollectionOrm,
    ProvisionQualityOrm,
)

logger = logging.getLogger(__name__)


@log_slow_execution(threshold_seconds=1.0)
def get_datasets(session: Session, datasets=None) -> List[DatasetModel]:
    query = (
        session.query(DatasetOrm)
        .filter(DatasetOrm.typology != "specification")
        .order_by(DatasetOrm.dataset)
    )

    if datasets:
        logger.debug(f"Filtering by {len(datasets)} datasets")
        query = query.filter(DatasetOrm.dataset.in_(datasets))

    dataset_results = query.all()
    logger.info(
        "Query executed successfully",
        extra={"num_results": len(dataset_results)},
    )
    return [DatasetModel.model_validate(ds) for ds in dataset_results]


@redis_cache("datasets", model_class=DatasetModel)
def get_all_datasets(session: DbSession) -> List[DatasetModel]:
    return get_datasets(session.session)


def get_dataset_query(session: Session, dataset) -> DatasetModel:
    dataset = session.query(DatasetOrm).get(dataset)
    if dataset is not None:
        return DatasetModel.model_validate(dataset)
    return None


def get_dataset_filter_fields(dataset: DatasetModel, fields: List[str]):
    return dataset.model_dump(include=set(fields))


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
    return [DatasetModel.model_validate(ds) for ds in datasets]


@redis_cache("datasets-typology-geo", model_class=DatasetModel)
def get_datasets_with_data_by_geography(session: DbSession) -> List[DatasetModel]:
    return get_datasets_with_data_by_typology(session.session, "geography")


def get_typologies(session: Session) -> List[TypologyModel]:
    typologies = session.query(TypologyOrm).order_by(TypologyOrm.typology).all()
    return [TypologyModel.model_validate(t) for t in typologies]


# returns all typologies with at least one dataset that falls under that typology


@redis_cache("typologies+entities", model_class=TypologyModel)
def get_typologies_with_entities(dbsession: DbSession) -> List[TypologyModel]:
    session = dbsession.session
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
    return [TypologyModel.model_validate(t) for t in typologies]


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
    return [OrganisationModel.model_validate(o) for o in organisations]


def get_providers_for_dataset(session: Session, dataset) -> List[ProviderModel]:
    """
    A provider is defined as an organisation with an active endpoint
    that does not have and enddate (i.e. is still in use) for this
    dataset (has_active_endpoint=True).
    """
    resolved_name = func.coalesce(
        ProvisionQualityOrm.organisation_name, OrganisationOrm.name
    )
    is_active_provider = ProvisionQualityOrm.has_active_endpoint.is_(True)

    results = (
        session.query(ProvisionQualityOrm, OrganisationOrm.entity, resolved_name)
        .outerjoin(
            OrganisationOrm,
            OrganisationOrm.organisation == ProvisionQualityOrm.organisation,
        )
        .filter(ProvisionQualityOrm.dataset == dataset)
        .filter(is_active_provider)
        .order_by(resolved_name)
        .all()
    )
    providers = []
    for provision_quality, entity, organisation_name in results:
        if not organisation_name:
            continue
        providers.append(
            ProviderModel(
                dataset=provision_quality.dataset,
                organisation=provision_quality.organisation,
                organisation_name=organisation_name,
                entity=entity,
                is_designated_provider=provision_quality.is_designated_provider,
                has_active_endpoint=provision_quality.has_active_endpoint,
                has_active_resource=provision_quality.has_active_resource,
                owns_entities=provision_quality.owns_entities,
                quality=provision_quality.quality,
                entity_count=provision_quality.entity_count,
                quality_score=provision_quality.quality_score,
            )
        )
    return providers


def get_latest_resource(session: Session, dataset) -> DatasetCollectionModel:
    result = session.query(DatasetCollectionOrm).get(dataset)
    if result is not None:
        return DatasetCollectionModel.model_validate(result)
    else:
        return None


def get_dataset_coverage_status(dataset: str) -> bool:
    with open("config/dataset_coverage.yml", "r") as file:
        coverage_data = yaml.safe_load(file)

    coverage_datasets = coverage_data.get("datasets_with_full_coverage", [])
    full_coverage = dataset in coverage_datasets

    return "full" if full_coverage else "partial"


def filter_datasets(session: Session, **kwargs):
    """
    Return datasets matching the provided filters.
    Only known dataset fields are applied; unknown filter keys are ignored.
    """
    filters = [
        getattr(DatasetOrm, key) == value
        for key, value in kwargs.items()
        if hasattr(DatasetOrm, key)
    ]
    dataset_results = session.query(DatasetOrm).filter(*filters).all()
    return [DatasetModel.model_validate(ds) for ds in dataset_results]
