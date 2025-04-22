from locust import HttpUser, task, tag, between
import random
import os
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


POOL_SIZE = int(os.getenv("URL_POOL_SIZE")) if os.getenv("URL_POOL_SIZE") else 100


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


POOL = create_url_pool(POOL_SIZE, default_param_modes, default_clamp_opts)


class RandomisedEntityUser(HttpUser):
    """Edit clamp opts to vary the numeber of params for each key"""

    wait_time = between(1, 3)

    modes = default_param_modes
    clamp_opts = default_clamp_opts
    pool = []

    def on_start(self):
        logger.info(f"Using pool size: {POOL_SIZE}")
        self.pool = create_url_pool(POOL_SIZE, self.modes, self.clamp_opts)

    def request_entities(self, url, name):
        with self.client.get(url, name=name, catch_response=True) as response:
            if response.status_code != 200:
                msg = f"status: {response.status_code} URL: {url}"
                logger.warning(msg)
                response.failure(msg)

    def get_entities(self, fmt):
        params = param_sample(self.modes, clamp=self.clamp_opts)
        params["organisation_entity"] = params["organisation"]
        params.pop("organisation")
        url = param_sample_to_url(params, format=fmt)
        self.request_entities(url, f"/entity, {fmt}")

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
        self.request_entities(url, "/entity (dynamic pool)")

    @task
    @tag("static")
    def get_entities_from_static_pool(self):
        url = random.choice(POOL)
        self.request_entities(url, "/entity (static pool)")
