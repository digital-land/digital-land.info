import logging
from application.data_access.os_api import search

logger = logging.getLogger(__name__)


def find_an_area(q: str):
    # Implementation for finding an area based on the search query
    search_query = (q or "").strip()
    search_result = None

    if not search_query:
        return None

    if search_query:
        try:
            search_response = search(search_query) or []
            type = "uprn" if search_query.isdigit() else "postcode"
            # If there are more than 2 results, choose the item in the middle
            # (user expectation: return the middle item for longer lists).
            if not search_response:
                result = None
            elif len(search_response) > 2:
                mid = len(search_response) // 2
                result = search_response[mid]
            else:
                # Keep existing behaviour for 1 or 2 items (first item)
                result = search_response[0]
            name = (
                (result.get("POSTCODE") if type == "postcode" else result.get("UPRN"))
                if result
                else None
            )

            search_result = {
                "type": type,
                "query": search_query,
                "result": result,
                "geometry": {
                    "name": name,
                    "type": "point",
                    "data": {
                        "type": "Point",
                        "coordinates": [result.get("LNG"), result.get("LAT")],
                        "properties": {
                            **result,
                            "name": name,
                        },
                    },
                }
                if result
                else None,
            }
        except Exception as e:
            logger.warning(f"Search failed for query '{search_query}': {str(e)}")
            # Continue without search result - the map will still render
            search_result = None

    return search_result
