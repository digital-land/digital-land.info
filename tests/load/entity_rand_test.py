from locust import HttpUser, task, tag, between
import random
import tests.load.data_entity as DE
from tests.load.utils import param_sample, param_sample_to_url


default_param_modes = {
    "typology": 3,
    "dataset": 2,
    "location": 3,
    "organisation": 3,
    "period": 1,
}


def create_url_pool(n, modes, clamp):
    pool = []
    for _ in range(n):
        fmt = random.choice(DE.FORMATS)
        params = param_sample(modes, clamp)
        params["organisation_entity"] = params["organisation"]
        params.pop("organisation")
        url = param_sample_to_url(params, format=fmt)
        pool.append(url)


class RandomisedEntityUser(HttpUser):
    """Edit clamp opts to vary the numeber of params for each key"""

    wait_time = between(1, 3)

    modes = default_param_modes
    clamp_opts = {"dataset": 3, "organisation": 2, "location": 4}
    pool = []

    def on_start(self):
        self.pool = create_url_pool(100, self.modes, self.clamp_opts)

    def get_entities(self, fmt):
        params = param_sample(self.modes, clamp=self.clamp_opts)
        params["organisation_entity"] = params["organisation"]
        params.pop("organisation")
        url = param_sample_to_url(params, format=fmt)
        self.client.get(url, name=f"/entity, {fmt}")

    @task
    def get_entities_json(self):
        self.get_entities(".json")

    @task
    def get_entities_html(self):
        self.get_entities(None)

    @task
    def get_entities_geojson(self):
        self.get_entities(".geojson")

    @tag("pooled_urls")
    @task
    def get_entities_pooled(self):
        fmt = random.choice(DE.FORMATS)
        params = param_sample(self.modes, self.clamp_opts)
        params["organisation_entity"] = params["organisation"]
        params.pop("organisation")

        url = param_sample_to_url(params, format=fmt)
        self.client.get(url, name=f"/entity (pooled URLs), {fmt}")
