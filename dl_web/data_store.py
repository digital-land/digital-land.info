import csv
import logging
import pathlib
import shutil
from pathlib import Path

import boto3
import botocore
from digital_land.collection import Collection
from digital_land.organisation import Organisation

logger = logging.getLogger(__name__)

collection_files = ["resource", "log", "source", "endpoint"]
organisation = Organisation("var/cache/organisation.csv")


class DataStore:
    def __init__(self):
        self.s3 = boto3.resource("s3")
        self.collection_bucket = self.s3.Bucket("collection-dataset")
        self.collections = set()
        self._collection = Collection(None, "var/cache")
        self.loaded = False

    def fetch_collections(self, schema_field, collections):
        for c in collections:
            if self.fetch_collection(c):
                self.collections.add(c)
        self.merge_collections(schema_field)

    def fetch_collection(self, name, use_cache=False):
        for file in collection_files:
            try:
                key = f"{name}-collection/collection/{file}.csv"
                path = pathlib.Path(f"var/cache/collection/{name}/{file}.csv")
                path.parent.mkdir(parents=True, exist_ok=True)
                self.s3.meta.client.download_file("collection-dataset", key, str(path))
            except botocore.exceptions.ClientError as e:
                if e.response["Error"]["Code"] == "404":
                    # The object does not exist.
                    if path.parent.exists():
                        logger.warn("removing dir %s", str(path.parent))
                        shutil.rmtree(str(path.parent))
                    return False
                else:
                    raise e

        # All collections files have been fetched successfully
        return True

    def merge_collections(self, schema_field):
        for filename in collection_files:
            file = pathlib.Path(f"var/cache/{filename}.csv")
            if file.exists():
                file.unlink()
            writer = csv.DictWriter(file.open("w"), fieldnames=schema_field[filename])
            writer.writeheader()
            for c in self.collections:
                self.add_collection_file(writer, c, filename)

    def add_collection_file(self, writer, collection, filename):
        path = pathlib.Path(f"var/cache/collection/{collection}/{filename}.csv")
        logger.info("merging %s", path)
        reader = csv.DictReader(path.open())
        for row in reader:
            writer.writerow(row)

    def load_collection(self):
        logger.info("loading collection")
        self._collection.load()
        self.loaded = True

    @property
    def collection(self):
        if not self.loaded:
            self.load_collection()
        return self._collection

    def fetch(self, collection_name, resource_hash, type_, use_cache=True):
        path = Path(f"var/cache/{type_}/{resource_hash}.csv")
        key = f"{collection_name}-collection/{type_}/{collection_name}/{resource_hash}.csv"

        if use_cache and path.exists():
            return path

        path.parent.mkdir(exist_ok=True)
        logger.warn("fetching %s", key)
        self.s3.meta.client.download_file("collection-dataset", key, str(path))
        return path

    # def fetch_resource(self, collection, resource_hash, use_cache=True):
    #     path = Path(f"var/cache/transformed/{resource_hash}.csv")
    #     key = f"{collection}-collection/transformed/{collection}/{resource_hash}.csv"
    #     return self.fetch(path, key, use_cache)

    # def fetch_issue(self, collection, resource_hash, use_cache=True):
    #     path = Path(f"var/cache/issue/{resource_hash}.csv")
    #     key = f"{collection}-collection/issue/{collection}/{resource_hash}.csv"
    #     return self.fetch(path, key, use_cache)


datastore = DataStore()
