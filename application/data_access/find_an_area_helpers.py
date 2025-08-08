import logging
from application.data_access.os_api import search

logger = logging.getLogger(__name__)


def find_an_area(q: str):
    # Implementation for finding an area based on the search query
    search_query = q.strip()
    search_result = None

    if search_query:
        try:
            search_response = search(search_query) or []
            type = "uprn" if search_query.isdigit() else "postcode"
            result = search_response[0] if len(search_response) else None
            name = (
                (result["POSTCODE"] if type == "postcode" else result["UPRN"])
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
                        "coordinates": [result["LNG"], result["LAT"]],
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