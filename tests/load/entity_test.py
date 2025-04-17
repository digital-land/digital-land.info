from locust import HttpUser, task, tag, between
from urllib.parse import urlencode
import random
from tests.load.data_entity import (
    TYPOLOGIES,
    DATASETS,
    LOCATIONS,
    ORGANISATIONS,
    PERIODS,
)
from tests.load.utils import skewed_random_triangular


class EntityLoadTestUser(HttpUser):
    wait_time = between(1, 3)

    valid_entity_id = 31000
    sample_dataset = "border"
    sample_typology = "geography"

    @task
    def get_entity_html(self):
        self.client.get(f"/entity/{self.valid_entity_id}")

    @task
    def get_entity_json(self):
        self.client.get(f"/entity/{self.valid_entity_id}.json")

    @task
    def get_entity_geojson(self):
        self.client.get(f"/entity/{self.valid_entity_id}.geojson")

    @task
    def search_entities_json(self):
        self.client.get(
            f"/entity.json?dataset={self.sample_dataset}&typology={self.sample_typology}"
        )

    @task
    def search_entities_geojson(self):
        self.client.get(
            f"/entity.geojson?dataset={self.sample_dataset}&typology={self.sample_typology}"
        )


data_tuples = [
    # DATA, key
    (TYPOLOGIES, "typology"),
    (DATASETS, "dataset"),
    (LOCATIONS, "location"),
    (ORGANISATIONS, "organisation"),
    (PERIODS, "period"),
]


default_param_modes = {
    "typology": 3,
    "dataset": 2,
    "location": 3,
    "organisation": 3,
    "period": 1,
}


def param_sample(modes=default_param_modes, clamp={}):
    """Returns a map of param names to collections of random samples of data (for given key).

    Optionally, a clamp map can be passed that limits the sample sizes for corresponding key.
    """
    params = {}
    for data, key in data_tuples:
        num = skewed_random_triangular(len(data) - 1, modes["typology"])
        if key in clamp:
            num = min(num, clamp[key])
        params[key] = random.sample(data, num)
    limit = random.randint(0, 100)
    if limit > 0:
        params["limit"] = limit
    return params


def param_sample_to_url(param_sample, format=".json"):
    assert format in [".json", ".geojson"]
    return f"/entity{format or ''}?{urlencode(param_sample, doseq=True)}"


FORMATS = [None, ".json", ".geojson"]


class EntityUser(HttpUser):
    wait_time = between(1, 3)
    modes = default_param_modes

    @tag("heavy")
    @task
    def typologies(self):
        params = param_sample(self.modes)
        fmt = random.choice(FORMATS)
        url = param_sample_to_url(params, format=None)
        self.client.get(url, name=f"/entity (heavy) {fmt}")


class LightEntityUser(HttpUser):
    wait_time = between(1, 3)
    modes = default_param_modes
    clamp_opts = {"dataset": 3, "organisation": 2, "location": 4}

    @tag("light")
    @task
    def typologies(self):
        params = param_sample(self.modes, clamp={})
        fmt = random.choice(FORMATS)
        url = param_sample_to_url(params, format=fmt)
        self.client.get(url, name=f"/entity (light), {fmt}")
