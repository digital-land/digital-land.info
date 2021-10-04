import logging
from pathlib import Path

import aiofiles
import aiohttp
import requests
from digital_land.collection import Collection
from digital_land.organisation import Organisation

logger = logging.getLogger(__name__)

collection_files = ["resource", "log", "source", "endpoint"]
base_url = "https://collection-dataset.s3.eu-west-2.amazonaws.com/"
resource_info_url = "https://datasette.digital-land.info/digital-land/resource_view_data.json?resource={resource_hash}"
organisation = Organisation("var/cache/organisation.csv")
datastore = None


class DataStore:
    def __init__(self):
        self.collections = set()
        self._collection = Collection(None, "var/cache")
        self.loaded = False

    async def _async_init(self):
        self.client = aiohttp.ClientSession()

    async def close_connection(self):
        await self.client.close()
        self.client = None

    def fetch_resource_info(self, resource_hash):
        with requests.get(
            resource_info_url.format(resource_hash=resource_hash)
        ) as resp:
            return resp.json()

    async def fetch(self, collection_name, resource_hash, type_, use_cache=True):
        path = Path(f"var/cache/{type_}/{resource_hash}.csv")
        key = f"{collection_name}-collection/{type_}/{collection_name}/{resource_hash}.csv"

        if use_cache and path.exists():
            return path

        logger.info("writing to %s", str(path))
        path.parent.mkdir(exist_ok=True)
        url = f"{base_url}{key}"
        logger.info("fetching %s", url)
        async with self.client.get(url) as response:
            logger.info("%s [%s]", url, response.status)
            if response.status == 200:
                f = await aiofiles.open(str(path), mode="wb")
                await f.write(await response.read())
                await f.close()
            else:
                logger.error(
                    "fetch of %s failed with status code %s", url, response.status
                )
                raise Exception(
                    "fetch of %s failed with status code %s" % (url, response.status)
                )
        return path

    # def fetch_resource(self, collection, resource_hash, use_cache=True):
    #     path = Path(f"var/cache/transformed/{resource_hash}.csv")
    #     key = f"{collection}-collection/transformed/{collection}/{resource_hash}.csv"
    #     return self.fetch(path, key, use_cache)


#     def fetch_issue(self, collection, resource_hash, use_cache=True):
#         path = Path(f"var/cache/issue/{resource_hash}.csv")
#         key = f"{collection}-collection/issue/{collection}/{resource_hash}.csv"
#         return self.fetch(collection, path, key, use_cache)


async def get_datastore():
    global datastore
    if datastore:
        logger.info("RETURNING EXISTING DATASTORE")
        return datastore
    logger.info("CREATING NEW DATASTORE")
    datastore = DataStore()
    await datastore._async_init()
    return datastore
