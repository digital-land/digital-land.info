import logging
import urllib.parse

from application.core.utils import get
from application.core.models import Dataset
from application.db.models import Dataset as DatasetModel
from application.db.session import get_context_session
from application.settings import get_settings

logger = logging.getLogger(__name__)


def fetch_datasets():
    with get_context_session() as session:
        datasets = session.query(DatasetModel).all()
        return [Dataset.from_orm(ds) for ds in datasets]


def fetch_dataset(dataset):
    with get_context_session() as session:
        dataset = session.query(DatasetModel).get(dataset)
        return Dataset.from_orm(dataset)


def fetch_datasets_with_theme():
    datasette_url = get_settings().DATASETTE_URL
    query_lines = [
        "SELECT DISTINCT dataset.dataset, dataset.name, dataset.plural, dataset.typology,",
        "(CASE WHEN pipeline.pipeline IS NOT NULL THEN 1 WHEN pipeline.pipeline IS NULL THEN 0 END) AS dataset_active,",
        "GROUP_CONCAT(dataset_theme.theme, ';') AS dataset_themes",
        "FROM dataset LEFT JOIN pipeline ON dataset.dataset = pipeline.pipeline",
        "INNER JOIN dataset_theme ON dataset.dataset = dataset_theme.dataset",
        "GROUP BY dataset.dataset",
        "ORDER BY dataset.name ASC",
    ]
    query_str = " ".join(query_lines)
    query = urllib.parse.quote(query_str)
    url = f"{datasette_url}/digital-land.json?sql={query}"
    logger.info("get_datasets_with_themes: %s", url)
    return get(url).json()


def fetch_datasets_with_typology(typology):
    datasette_url = get_settings().DATASETTE_URL
    url = f"{datasette_url}/digital-land/dataset.json?_shape=object&_sort=dataset&typology__exact={typology}"
    logger.info("get_datasets_with_typology: %s", url)
    return get(url).json()


def fetch_typologies():
    datasette_url = get_settings().DATASETTE_URL
    url = f"{datasette_url}/digital-land/typology.json"
    logger.info("get_typologies: %s", url)
    return get(url).json()


def fetch_local_authorities():
    datasette_url = get_settings().DATASETTE_URL
    query_str = """select * from organisation where organisation like '%local-authority-eng%' order by organisation"""
    query = urllib.parse.quote(query_str)
    url = f"{datasette_url}/digital-land.json?sql={query}"
    logger.info("get_local_authorities: %s", url)
    return get(url).json()


def fetch_publisher_coverage_count(dataset):
    datasette_url = get_settings().DATASETTE_URL
    query_lines = [
        "SELECT",
        "count(DISTINCT source.organisation) as expected_publishers,",
        "COUNT(DISTINCT CASE WHEN source.endpoint != '' THEN source.organisation END) AS publishers",
        "FROM",
        "source",
        "INNER JOIN source_pipeline on source.source = source_pipeline.source",
        "WHERE",
        f"source_pipeline.pipeline = '{dataset}'",
    ]
    query_str = " ".join(query_lines)
    query = urllib.parse.quote(query_str)
    url = f"{datasette_url}/digital-land.json?sql={query}"
    logger.info("get_publisher_coverage_count: %s", url)
    return get(url).json()


def fetch_latest_resource(dataset):
    datasette_url = get_settings().DATASETTE_URL
    query_lines = [
        "SELECT",
        "resource.resource,",
        "resource.end_date,",
        "resource.entry_date,",
        "resource.start_date,",
        "source_pipeline.pipeline",
        "FROM",
        "resource",
        "INNER JOIN resource_endpoint ON resource.resource = resource_endpoint.resource",
        "INNER JOIN source ON resource_endpoint.endpoint = source.endpoint",
        "INNER JOIN source_pipeline ON source.source = source_pipeline.source",
        "WHERE",
        f"source_pipeline.pipeline = '{dataset}'",
        "ORDER BY",
        "resource.start_date DESC",
        "LIMIT 1",
    ]
    query_str = " ".join(query_lines)
    query = urllib.parse.quote(query_str)
    url = f"{datasette_url}/digital-land.json?sql={query}"
    logger.info("get_publisher_coverage_count: %s", url)
    return get(url).json()


def fetch_lastest_log_date(dataset):
    datasette_url = get_settings().DATASETTE_URL
    query_lines = [
        "SELECT",
        "source_pipeline.pipeline,",
        "MAX(log.entry_date) AS latest_attempt",
        "FROM",
        "source",
        "INNER JOIN source_pipeline ON source.source = source_pipeline.source",
        "INNER JOIN log ON source.endpoint = log.endpoint",
        "WHERE",
        f"source_pipeline.pipeline = '{dataset}'",
        "GROUP BY",
        "source_pipeline.pipeline",
    ]
    query_str = " ".join(query_lines)
    query = urllib.parse.quote(query_str)
    url = f"{datasette_url}/digital-land.json?sql={query}"
    logger.info("get_latest_log_date: %s", url)
    return get(url).json()
