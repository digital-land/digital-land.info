import requests
import os

def get_os_api_key():
    return os.getenv("OS_CLIENT_KEY")

def search_postcode(query: str):
    url = "https://api.os.uk/search/places/v1/postcode"
    params = {
        "postcode": query,
        "key": get_os_api_key(),
    }
    response = requests.get(url, params=params)
    return response.json()

def search_uprn(query: str):
    url = "https://api.os.uk/search/places/v1/uprn"
    params = {
        "uprn": query,
        "key": get_os_api_key(),
    }
    response = requests.get(url, params=params)
    return response.json()

def transform_search_results(results: dict):
    return [
        result.get("DPA", {})
        for result in results.get("results", [])
    ]

def search(query: str):
    if query.isdigit():
        return transform_search_results(search_uprn(query))
    else:
        return transform_search_results(search_postcode(query))
