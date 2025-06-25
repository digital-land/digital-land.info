import requests
import os
import re


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

def transform_search_results(results: dict):
    if not results or not isinstance(results, dict):
        return []
    results_list = results.get("results", [])
    if results_list is None:
        return []
    return [result.get("DPA", {}) for result in results_list]

def search(query: str):
    type = "uprn" if query.isdigit() else "postcode"

    if len(query.strip()) == 0 or (type == "postcode" and not is_valid_postcode(query.strip())):
        return []

    results = search_uprn(query) if type == "uprn" else search_postcode(query)
    if results is None or not isinstance(results, dict):
        return []
    return transform_search_results(results)
