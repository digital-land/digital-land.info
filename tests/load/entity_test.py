from locust import HttpUser, task, between
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class EntityLoadTestUser(HttpUser):
    wait_time = between(1, 3)

    valid_entity_id = 31000
    sample_dataset = "border"
    sample_typology = "geography"

    @task
    def get_entity_html(self):
        url = f"/entity/{self.valid_entity_id}"
        with self.client.get(url, catch_response=True) as response:
            if response.status_code != 200:
                msg = f"Failure response for URL: {url}, Status: {response.status_code}"
                logger.warning(msg)
                response.failure(msg)

    @task
    def get_entity_json(self):
        url = f"/entity/{self.valid_entity_id}.json"
        with self.client.get(url, catch_response=True) as response:
            if response.status_code != 200:
                msg = f"Failure response for URL: {url}, Status: {response.status_code}"
                logger.warning(msg)
                response.failure(msg)

    @task
    def get_entity_geojson(self):
        url = f"/entity/{self.valid_entity_id}.geojson"
        with self.client.get(url, catch_response=True) as response:
            if response.status_code != 200:
                msg = f"Failure response for URL: {url}, Status: {response.status_code}"
                logger.warning(msg)
                response.failure(msg)

    @task
    def search_entities_json(self):
        url = f"/entity.json?dataset={self.sample_dataset}&typology={self.sample_typology}"
        with self.client.get(url, catch_response=True) as response:
            if response.status_code != 200:
                msg = f"Failure response for URL: {url}, Status: {response.status_code}"
                logger.warning(msg)
                response.failure(msg)

    @task
    def search_entities_geojson(self):
        url = f"/entity.geojson?dataset={self.sample_dataset}&typology={self.sample_typology}"
        with self.client.get(url, catch_response=True) as response:
            if response.status_code != 200:
                msg = f"Failure response for URL: {url}, Status: {response.status_code}"
                logger.warning(msg)
                response.failure(msg)
