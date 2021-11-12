from typing import List

import aiohttp
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
