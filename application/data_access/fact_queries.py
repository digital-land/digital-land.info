import logging
from typing import List

import requests

from application.core.models import EntityModel, FactModel
from application.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def get_entity_facts(entity: EntityModel) -> List[FactModel]:
    url = f"{settings.DATASETTE_URL}/{entity.dataset}/fact.json"
    params = {"entity__exact": entity.entity, "_shape": "array", "_labels": "off"}
    try:
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        rows = resp.json()
        # datasette returns empty strings for nulls. is there
        # a way to prevent this? for now filter out empties
        for r in rows:
            for key, val in r.items():
                if not val:
                    r[key] = None
        facts = [FactModel(**fact) for fact in rows]
        return facts
    except Exception as e:
        logger.exception(e)
        return []
