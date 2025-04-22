from locust import HttpUser, task, tag, between
import random
import tests.load.data_entity as DE
from tests.load.utils import param_sample, param_sample_to_url

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

default_param_modes = {
    "typology": 3,
    "dataset": 2,
    "location": 3,
    "organisation": 3,
    "period": 1,
}

default_clamp_opts = {"dataset": 3, "organisation": 2, "location": 4}


def create_url_pool(n, modes, clamp):
    pool = []
    for _ in range(n):
        fmt = random.choice(DE.FORMATS)
        params = param_sample(modes, clamp)
        params["organisation_entity"] = params["organisation"]
        params.pop("organisation")
        url = param_sample_to_url(params, format=fmt)
        pool.append(url)
    return pool


POOL = create_url_pool(100, default_param_modes, default_clamp_opts)


class RandomisedEntityUser(HttpUser):
    """Edit clamp opts to vary the numeber of params for each key"""

    wait_time = between(1, 3)

    modes = default_param_modes
    clamp_opts = default_clamp_opts
    pool = []

    def on_start(self):
        self.pool = create_url_pool(100, self.modes, self.clamp_opts)

    def get_entities(self, fmt):
        params = param_sample(self.modes, clamp=self.clamp_opts)
        params["organisation_entity"] = params["organisation"]
        params.pop("organisation")
        url = param_sample_to_url(params, format=fmt)
        with self.client.get(
            url, name=f"/entity, {fmt}", catch_response=True
        ) as response:
            if response.status_code != 200:
                msg = f"Failure response for URL: {url}"
                logger.warning(msg)
                response.failure(msg)

    @task
    @tag("random")
    def get_entities_json(self):
        self.get_entities(".json")

    @task
    @tag("random")
    def get_entities_html(self):
        self.get_entities(None)

    @task
    @tag("random")
    def get_entities_geojson(self):
        self.get_entities(".geojson")

    @task
    @tag("random")
    def get_entities_from_dynamic_pool(self):
        url = random.choice(self.pool)
        with self.client.get(
            url, name="/entity (dynamic pool)", catch_response=True
        ) as response:
            if response.status_code != 200:
                msg = f"Failure response for URL: {url} (dynamic pool)"
                logger.warning(msg)
                response.failure(msg)

    @task
    @tag("static")
    def get_entities_from_static_pool(self):
        url = random.choice(POOL)
        with self.client.get(
            url, name="/entity (static pool)", catch_response=True
        ) as response:
            if response.status_code != 200:
                msg = f"Failure response for URL: {url} (static pool)"
                logger.warning(msg)
                response.failure(msg)
