from locust import HttpUser, task, between
from tests.load.data import DATASETS

class CacheWarmupUser(HttpUser):
    wait_time = between(1, 3)  # defines a random delay between requests

    @task
    def load_home_page(self):
        self.client.get("/", name="Home page")

    @task
    def load_about_page(self):
        self.client.get("/about")

    @task
    def load_api_page(self):
        self.client.get("/docs")

    @task
    def load_entity_html(self):
        self.client.get("/entity")

    @task
    def load_entity_json(self):
        self.client.get("/entity.json")

    @task
    def load_entity_geojson(self):
        self.client.get("/entity.geojson")

    @task
    def load_local_plan_boundary_html(self):
        self.client.get("/entity/?dataset=local-plan-boundary")

    @task
    def load_local_plan_boundary_json(self):
        self.client.get("/entity.json?dataset=local-plan-boundary")

    @task
    def load_local_plan_boundary_geojson(self):
        self.client.get("/entity.geojson?dataset=local-plan-boundary")

    @task
    def load_map_html(self):
        self.client.get("/map")

    @task
    def list_datasets_html(self):
        self.client.get("/dataset")

    @task
    def list_datasets_json(self):
        self.client.get("/dataset.json")

    @task
    def load_each_dataset(self):
        for dataset in DATASETS:
            url = f"/dataset/{dataset}"
            self.client.get(url)
