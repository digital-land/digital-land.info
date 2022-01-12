import logging
import urllib.parse

from application.core.utils import get
from application.core.models import DatasetModel
from application.db.models import DatasetOrm, EntityOrm
from application.db.session import get_context_session
from application.settings import get_settings

logger = logging.getLogger(__name__)


def get_datasets():
    with get_context_session() as session:
        datasets = session.query(DatasetOrm).order_by(DatasetOrm.dataset).all()
        return [DatasetModel.from_orm(ds) for ds in datasets]


def get_dataset_query(dataset):
    with get_context_session() as session:
        dataset = session.query(DatasetOrm).get(dataset)
        return DatasetModel.from_orm(dataset)


def get_datasets_with_data_by_typology(typology):
    from sqlalchemy import select
    from sqlalchemy import func

    sql = select(
        DatasetOrm, func.count(func.distinct(EntityOrm.entity)).label("entity_count")
    )
    sql = sql.filter(DatasetOrm.typology == typology)
    sql = sql.filter(DatasetOrm.dataset == EntityOrm.dataset)
    sql = sql.group_by(DatasetOrm.dataset)

    with get_context_session() as session:
        result = session.execute(sql)
        datasets = result.fetchall()
        return [DatasetModel.from_orm(ds.DatasetOrm) for ds in datasets]


# TODO - recreate from db
def fetch_typologies():
    datasette_url = get_settings().DATASETTE_URL
    url = f"{datasette_url}/digital-land/typology.json"
    logger.info("get_typologies: %s", url)
    return get(url).json()


# TODO - recreate from db
def fetch_local_authorities():
    datasette_url = get_settings().DATASETTE_URL
    query_str = """select * from organisation where organisation like '%local-authority-eng%' order by organisation"""
    query = urllib.parse.quote(query_str)
    url = f"{datasette_url}/digital-land.json?sql={query}"
    logger.info("get_local_authorities: %s", url)
    return get(url).json()


# TODO - recreate from db
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


# TODO - recreate from db
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


# TODO - recreate from db
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
