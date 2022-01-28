import copy
import json
import typing
import urllib
from typing import List

import requests
from pydantic import BaseModel
from datetime import date

from starlette.responses import Response


def create_dict(keys_list, values_list):
    zip_iterator = zip(keys_list, values_list)
    return dict(zip_iterator)


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


# Sets Nones to empty string in json encoding


def none_to_empty_str(d):
    copied = copy.deepcopy(d)
    if isinstance(copied, dict):
        for key, val in copied.items():
            copied[key] = none_to_empty_str(val)
    if isinstance(copied, list):
        for key, val in enumerate(copied):
            copied[key] = none_to_empty_str(val)
    if d is None:
        copied = ""
    return copied


class NoneToEmptyStringEncoder(json.JSONEncoder):
    def encode(self, obj):
        data = none_to_empty_str(obj)
        return super().encode(data)


class DigitalLandJSONResponse(Response):
    media_type = "application/json"

    def render(self, content: typing.Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            cls=NoneToEmptyStringEncoder,
        ).encode("utf-8")
