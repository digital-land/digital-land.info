import logging
import requests

from typing import List
from application.core.models import EntityModel, FactResourceModel
from application.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def get_entity_facts(entity: EntityModel) -> List[FactResourceModel]:
    url = f"{settings.DATASETTE_URL}/{entity.dataset}.json"
    sql = f"""SELECT f.*,
                     fr.resource,
                     fr.entry_number,
                     fr.entry_date AS resource_entry_date,
                     fr.start_date AS resource_start_date
            FROM fact f, fact_resource fr
            WHERE f.fact = fr.fact
            AND f.entity = {entity.entity};"""
    params = {"sql": sql, "_shape": "array"}
    try:
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        rows = resp.json()
        # datasette returns empty strings for nulls. is there
        # a datasette config way to prevent this? for now set empties
        # to None.
        for r in rows:
            for key, val in r.items():
                if not val:
                    r[key] = None
        facts = [FactResourceModel(**fact) for fact in rows]
        return facts
    except Exception as e:
        logger.exception(e)
        return []
