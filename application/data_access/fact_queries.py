import logging
import requests

from typing import List, Optional
from application.core.models import FactModel, DatasetFieldModel
from application.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def get_dataset_fields(dataset):
    url = f"{settings.DATASETTE_URL}/{dataset}.json"
    sql = """
         SELECT DISTINCT field
         FROM fact;
    """
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
        fields = [DatasetFieldModel(**field) for field in rows]
        return fields
    except Exception as e:
        logger.exception(e)
        return None


def get_fact_query(fact: str, dataset: str) -> Optional[FactModel]:
    url = f"{settings.DATASETTE_URL}/{dataset}.json"
    sql = f"""SELECT
                f.fact,
                f.entity,
                e.name as entity_name,
                e.prefix as entity_prefix,
                e.reference as entity_reference,
                f.reference_entity,
                f.field,
                f.value,
                min(fr.entry_date) as earliest_entry_date,
                max(fr.entry_date) as latest_entry_date,
                fr.resource as latest_resource,
                json_group_array(json_object('resource',fr.resource,'entry_date',fr.entry_date)) as resources
            FROM fact f, fact_resource fr, entity e
            WHERE f.fact = fr.fact
            AND f.entity = e.entity
            AND f.fact = '{fact}'
            GROUP BY f.entity, f.fact, f.field,f.value;"""

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
        return None


def get_search_facts_query(query_params: List) -> Optional[FactModel]:
    """
    A function that can take a single entity and retrieve all facts related to it.
    """
    # now using the entity information retrieve the facts for the entity
    url = f"{settings.DATASETTE_URL}/{query_params['dataset']}.json"
    sql = f"""SELECT
                f.fact,
                f.entity,
                e.name as entity_name,
                e.prefix as entity_prefix,
                e.reference as entity_reference,
                f.reference_entity,
                f.field,
                f.value,
                min(fr.entry_date) as earliest_entry_date,
                max(fr.entry_date) as latest_entry_date,
                fr.resource as latest_resource
            FROM fact f, fact_resource fr, entity e
            WHERE f.fact = fr.fact
            AND f.entity = e.entity
            AND f.entity = {query_params['entity']}"""

    if query_params["field"]:
        sql = (
            sql
            + f"""
        AND f.field in ('{"','".join(query_params['field'])}')
        """
        )

    sql = (
        sql
        + """
        GROUP BY f.entity, f.fact, f.field,f.value;
    """
    )
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
