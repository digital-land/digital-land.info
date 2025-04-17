import os
import random
from locust import HttpUser, task
from urllib.parse import urlencode
import load.data as data

TEST_SEED = int(os.getenv("TEST_SEED")) if os.getenv("TEST_SEED") else 2025
MAP_NUM_DATASET_TARGET = (
    int(os.getenv("MAP_NUM_DATASET_TARGET"))
    if os.getenv("MAP_NUM_DATASET_TARGET")
    else 5
)


def skewed_random_triangular(N, target=5):
    return round(random.triangular(0, N, target))


class MapUser(HttpUser):
    """Accesses the /map endpoint with a number of 'dataset' query params.

    Use `MAP_NUM_DATASET_TARGET` env variable to set the mode of the distribution (int)
    """

    @task
    def entity_page(self):
        num = skewed_random_triangular(
            len(data.MAP_DATASETS) - 1, target=MAP_NUM_DATASET_TARGET
        )
        datasets = random.sample(data.MAP_DATASETS, num)
        query_params = {"dataset": datasets}
        path = f"/entity/?{urlencode(query_params, doseq=True)}"
        # print(f"num: {num}, path: {path}")
        self.client.get(path, name=f"/entity N={num}")
