from locust import HttpUser, task, between
from tests.load.data import DATASETS, MAP_DATASETS


class CacheWarmupUser(HttpUser):
    wait_time = between(1, 3)  # defines a random delay between requests
    urls = [
        "/",
        "/about",
        "/about/roadmap",
        "/about/performance",
        "/about/contact",
        "/accessibility-statement",
        "/terms-and-conditions",
        "/docs",
        "/entity",
        "/entity.json",
        "/entity.geojson",
        "/map",
        "/dataset",
        "/dataset.json",
        *[f"/dataset/{dataset}" for dataset in DATASETS],
        *[f"/entity/?dataset={dataset}" for dataset in DATASETS],
        *[f"/entity.json?dataset={dataset}" for dataset in DATASETS],
        *[f"/entity.geojson?dataset={dataset}" for dataset in DATASETS],
        *[f"/map?dataset={dataset}" for dataset in MAP_DATASETS],
    ]

    @task
    def load_urls(self):
        for url in self.urls:
            self.client.get(url)
