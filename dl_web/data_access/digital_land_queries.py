import logging
import urllib.parse

from dl_web.resources import fetch
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
    return await fetch(url)


async def get_datasets_with_theme():
    datasette_url = get_settings().DATASETTE_URL
    url = "".join(
        [
            f"{datasette_url}/digital-land.json?sql=SELECT%0D%0A++DISTINCT+dataset.dataset%2C%0D%0A++",
            "dataset.name%2C%0D%0A++dataset.plural%2C%0D%0A++dataset.typology%2C%0D%0A++%28%0D%0A++++CASE%0D%0A++++",
            "++WHEN+pipeline.pipeline+IS+NOT+NULL+THEN+1%0D%0A++++++WHEN+pipeline.pipeline+IS+NULL+THEN+0%0D%0A++++",
            "END%0D%0A++%29+AS+dataset_active%2C%0D%0A++GROUP_CONCAT%28dataset_theme.theme%2C+%22%3B%22%29+AS+dataset_themes",
            "%0D%0AFROM%0D%0A++dataset%0D%0A++LEFT+JOIN+pipeline+ON+dataset.dataset+%3D+pipeline.pipeline%0D%0A++INNER+JOIN+",
            "dataset_theme+ON+dataset.dataset+%3D+dataset_theme.dataset%0D%0Agroup+by%0D%0A++dataset.dataset%0D%0Aorder+",
            "by%0D%0Adataset.name+ASC",
        ]
    )
    logger.info("get_datasets_with_themes: %s", url)
    return await fetch(url)


async def get_typologies():
    datasette_url = get_settings().DATASETTE_URL
    url = f"{datasette_url}/digital-land/typology.json"
    logger.info("get_typologies: %s", url)
    return await fetch(url)


async def get_local_authorities():
    datasette_url = get_settings().DATASETTE_URL
    url = "".join(
        (
            f"{datasette_url}/digital-land.json?sql=select%0D%0A++addressbase_custodian%2C%0D%0A++billing_authority",
            "%2C%0D%0A++census_area%2C%0D%0A++combined_authority%2C%0D%0A++company%2C%0D%0A++end_date%2C%0D%0A++entity",
            "%2C%0D%0A++entry_date%2C%0D%0A++esd_inventory%2C%0D%0A++local_authority_type%2C%0D%0A++",
            "local_resilience_forum%2C%0D%0A++name%2C%0D%0A++official_name%2C%0D%0A++opendatacommunities_area",
            "%2C%0D%0A++opendatacommunities_organisation%2C%0D%0A++organisation%2C%0D%0A++region",
            "%2C%0D%0A++shielding_hub%2C%0D%0A++start_date%2C%0D%0A++statistical_geography%2C%0D%0A++twitter",
            "%2C%0D%0A++website%2C%0D%0A++wikidata%2C%0D%0A++wikipedia%0D%0Afrom%0D%0A++organisation%0D%0Awhere",
            "%0D%0A++%22organisation%22+like+%22%25local-authority-eng%25%22%0D%0Aorder+by%0D%0A++organisation%0D%0A&p0",
            "=%25local-authority-eng%25",
        )
    )
    logger.info("get_local_authorities: %s", url)
    return await fetch(url)
