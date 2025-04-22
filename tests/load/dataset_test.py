from locust import HttpUser, tag, task, between
import random
from tests.load.data import DATASETS
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class DatasetLoadTestUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def list_datasets_html(self):
        self.client.get("/dataset")

    @task
    def list_datasets_json(self):
        self.client.get("/dataset.json")

    @task
    @tag("random")
    def get_dataset(self):
        dataset = random.choice(DATASETS)
        url = f"/dataset/{dataset}"
        with self.client.get(url, catch_response=True) as response:
            if response.status_code != 200:
                msg = f"Failure response for URL: {url}, Status: {response.status_code}"
                logger.warning(msg)
                response.failure(msg)
