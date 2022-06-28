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


def make_links(scheme, netloc, path, query, data):
    """
    Creates a set of links for use on the entity search page
    including extracting additional information of the data itself
    Arguments:
        scheme: str
        netloc: str
        path: str
        query: query string of incoming request
        data: dict that contains all the required data for a search query see get_entity_search
    """

    from urllib.parse import urlunsplit

    count = data["count"]
    limit = data["params"].get("limit", 10)
    offset = data["params"].get("offset", 0)

    # note api validation ensures limit > 0 but handle ZeroDivisionError
    try:
        page_count = count / limit
    except ZeroDivisionError:
        return {}

    last_offset = int(page_count) * limit
    next_offset = offset + limit
    prev_offset = offset - limit if offset else 0

    if count == 0 or count <= limit:
        # no pagination links needed
        return {}

    query_str = make_pagination_query_str(query, limit)
    pagination_links = {"first": urlunsplit((scheme, netloc, path, query_str, ""))}

    if 0 < last_offset <= count:
        query_str = make_pagination_query_str(query, limit, offset=last_offset)
        pagination_links["last"] = urlunsplit((scheme, netloc, path, query_str, ""))

    if next_offset < count and next_offset <= last_offset:
        query_str = make_pagination_query_str(query, limit, offset=next_offset)
        pagination_links["next"] = urlunsplit((scheme, netloc, path, query_str, ""))

    if offset != 0 and prev_offset >= 0:
        query_str = make_pagination_query_str(query, limit, offset=prev_offset)
        pagination_links["prev"] = urlunsplit((scheme, netloc, path, query_str, ""))

    return pagination_links


def make_pagination_query_str(query, limit, offset=0):
    from urllib.parse import parse_qs, urlencode

    query_dict = parse_qs(query)
    if "limit" not in query_dict:
        query_dict["limit"] = limit
    if offset != 0:
        query_dict["offset"] = offset
    else:
        query_dict.pop("offset", None)

    return urlencode(query_dict, doseq=True)


def to_snake(string: str) -> str:
    return string.replace("-", "_")


ENTITY_ATTRIBUTE_ORDER = {
    "reference": 0,
    "prefix": 1,
    "name": 2,
    "dataset": 3,
    "organisation-entity": 4,
    "start-date": 5,
    "end-date": 6,
    "entry-date": 7,
    "typology": 8,
    "geometry": 9,
    "point": 10,
}


def entity_attribute_sort_key(val, sort_order=ENTITY_ATTRIBUTE_ORDER):
    if isinstance(val, str):
        try:
            return sort_order[val]
        except KeyError:
            return len(sort_order)
    else:
        raise ValueError("Value provided is not a string")
