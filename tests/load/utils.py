import random
from urllib.parse import urlencode
from tests.load.data_entity import data_tuples, FORMATS


def skewed_random_triangular(N, target=5):
    return round(random.triangular(0, N, target))


def param_sample(modes, clamp={}):
    """Returns a map of param names to collections of random samples of data (for given key).

    Optionally, a clamp map can be passed that limits the sample sizes for corresponding key.
    """
    params = {}
    for data, key in data_tuples:
        n = len(data) - 1
        if key in clamp:
            n = min(n, clamp[key])
        num = skewed_random_triangular(n, modes["typology"])
        params[key] = random.sample(data, num)
    limit = random.randint(0, 100)
    if limit > 0:
        params["limit"] = limit
    return params


def param_sample_to_url(param_sample, format=".json"):
    assert format in FORMATS
    return f"/entity{format or ''}?{urlencode(param_sample, doseq=True)}"
