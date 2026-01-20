import logging
import os
import re
import requests

from typing import List, Dict

from application.data_access.entity_queries import get_entity_map_lpa
from application.db.session import get_context_session


logger = logging.getLogger(__name__)


def is_valid_postcode(query: str):
    postcode_regex = re.compile(r"^[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}$", re.IGNORECASE)
    return postcode_regex.match(query.strip())


def get_os_api_key():
    return os.getenv("OS_CLIENT_KEY")


def base_search_params():
    return {
        "key": get_os_api_key(),
        "output_srs": "WGS84",
    }


def search_postcode(query: str):
    try:
        url = "https://api.os.uk/search/places/v1/postcode"
        params = {
            **base_search_params(),
            "postcode": query,
        }
        response = requests.get(url, params=params)
        return response.json()
    except Exception:
        return None


def search_uprn(query: str):
    try:
        url = "https://api.os.uk/search/places/v1/uprn"
        params = {
            **base_search_params(),
            "uprn": query,
        }
        response = requests.get(url, params=params)
        return response.json()
    except Exception:
        return None


def transform_search_results(results: dict, search_type: str = ""):
    if search_type == "lpa":
        return [results] if isinstance(results, dict) else []

    if not results or not isinstance(results, dict):
        return []
    results_list = results.get("results", [])

    if results_list is None:
        return []
    return [result.get("DPA", {}) for result in results_list]


def search_local_planning_authority(query: str) -> List[Dict]:
    try:
        with get_context_session() as session:
            entity = get_entity_map_lpa(session, {"name": query})
    except Exception as exc:
        logger.info(
            "search_local_planning_authority(): entity NOT FOUND for '%s': %s",
            query,
            exc,
        )
        return []

    return entity.dict() if entity else {}


def search(query: str, search_type: str):
    if not query:
        return []

    results = None
    if search_type == "uprn":
        results = search_uprn(query)
    elif search_type == "lpa":
        results = search_local_planning_authority(query)
    else:
        if not is_valid_postcode(query):
            return []
        results = search_postcode(query)

    if results is None or not isinstance(results, dict):
        return []

    return transform_search_results(results, search_type)
