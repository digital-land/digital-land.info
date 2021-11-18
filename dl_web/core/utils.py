import urllib
from typing import List

import aiohttp
import requests
from pydantic import BaseModel
from datetime import date


def create_dict(keys_list, values_list):
    zip_iterator = zip(keys_list, values_list)
    return dict(zip_iterator)


async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.json()


# Used to customize jinja tojson filter
def model_dumps(obj, *args, **kwargs):
    import json

    items = []
    if isinstance(obj, List):
        for m in obj:
            items.append(json.loads(m.json()))
        return json.dumps(items, *args, **kwargs)
    if isinstance(obj, BaseModel):
        return obj.json()
    if isinstance(obj, date):
        return json.dumps(obj.__str__(), *args, **kwargs)
    else:
        return json.dumps(obj, *args, **kwargs)


def make_url(url: str, params: dict) -> str:
    _params = ["_shape=objects"]
    for k, v in params.items():
        k = urllib.parse.quote(k)
        if isinstance(v, str):
            v = urllib.parse.quote(v)
        _params.append(f"{k}={v}")
    url = f"{url}?{'&'.join(_params)}"
    return url


def get(url: str) -> requests.Response:
    try:
        response = requests.get(url)
    except ConnectionRefusedError:
        raise ConnectionError("failed to connect at %s" % url)
    return response
