import logging
import requests

from typing import List
from application.core.models import EntityModel, FactResourceModel, FactModel
from application.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def get_entity_fact_resources(entity: EntityModel) -> List[FactResourceModel]:
    url = f"{settings.DATASETTE_URL}/{entity.dataset}.json"
    sql = f"""SELECT f.*,
                     fr.resource,
                     fr.entry_number,
                     fr.entry_date AS resource_entry_date,
                     fr.start_date AS resource_start_date
            FROM fact f, fact_resource fr
            WHERE f.fact = fr.fact
            AND f.entity = {entity.entity}
            ORDER BY f.entry_date;"""
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


def get_entity_facts_query(entity: EntityModel) -> List[FactModel]:
    """
    A function that can take a single entity and retrieve all facts related to it.
    """
    # now using the entity information retrieve the facts for the entity
    url = f"{settings.DATASETTE_URL}/{entity.dataset}.json"
    sql = f"""SELECT f.entity,
                f.fact,
                f.field,
                f.value,
                min(fr.entry_date) as earliest_entry_date,
                max(fr.entry_date) as latest_entry_date,
                json_group_array(json_object('resource',fr.resource,'entry_date',fr.entry_date)) as resource_history
            FROM fact f, fact_resource fr
            WHERE f.fact = fr.fact
            AND f.entity = {entity.entity}
            GROUP BY f.entity, f.fact, f.field,f.value
            ORDER BY  f.field, f.entry_date;"""

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
        facts = [FactModel(**fact) for fact in rows]
        return facts
    except Exception as e:
        logger.exception(e)
        return []
