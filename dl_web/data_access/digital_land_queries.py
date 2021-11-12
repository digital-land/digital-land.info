import logging
import urllib.parse

from dl_web.core.utils import fetch
from dl_web.core.models import Dataset
from dl_web.settings import get_settings

logger = logging.getLogger(__name__)


async def get_datasets():
    datasette_url = get_settings().DATASETTE_URL
    url = f"{datasette_url}/digital-land/dataset.json?_shape=object"
    logger.info("get_datasets: %s", url)
    return await fetch(url)


async def get_dataset(dataset):
    datasette_url = get_settings().DATASETTE_URL
    url = f"{datasette_url}/digital-land/dataset.json?_shape=object&dataset={urllib.parse.quote(dataset)}"
    logger.info("get_dataset: %s", url)
    data = await fetch(url)
    for key, val in data[dataset].items():
        if isinstance(val, str) and not val:
            data[dataset][key] = None
    return Dataset(**data[dataset])


async def get_datasets_with_theme():
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
    return await fetch(url)


async def get_typologies():
    datasette_url = get_settings().DATASETTE_URL
    url = f"{datasette_url}/digital-land/typology.json"
    logger.info("get_typologies: %s", url)
    return await fetch(url)


async def get_local_authorities():
    datasette_url = get_settings().DATASETTE_URL
    query_str = """select * from organisation where organisation like '%local-authority-eng%' order by organisation"""
    query = urllib.parse.quote(query_str)
    url = f"{datasette_url}/digital-land.json?sql={query}"
    logger.info("get_local_authorities: %s", url)
    return await fetch(url)
