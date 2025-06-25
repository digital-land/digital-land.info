import requests
import os

def get_os_api_key():
    return os.getenv("OS_CLIENT_KEY")

def base_search_params():
    return {
        "key": get_os_api_key(),
        "output_srs": "WGS84",
    }

def search_postcode(query: str):
    url = "https://api.os.uk/search/places/v1/postcode"
    params = {
        **base_search_params(),
        "postcode": query,
    }
    response = requests.get(url, params=params)
    return response.json()

def search_uprn(query: str):
    url = "https://api.os.uk/search/places/v1/uprn"
    params = {
        **base_search_params(),
        "uprn": query,
    }
    response = requests.get(url, params=params)
    return response.json()

def transform_search_results(results: dict):
    return [
        result.get("DPA", {})
        for result in results.get("results", [])
    ]

def search(query: str):
    results = search_uprn(query) if query.isdigit() else search_postcode(query)
    return transform_search_results(results)
