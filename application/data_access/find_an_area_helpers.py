import logging
from application.data_access.os_api import search

logger = logging.getLogger(__name__)


def find_an_area(search_query: str):
    # Implementation for finding an area based on the search query

    if not search_query:
        return None

    if search_query:
        try:
            string_no_spaces = search_query.replace(" ", "")

            if string_no_spaces.isdigit():
                search_type = "uprn"
            elif string_no_spaces.isalpha():
                search_type = "lpa"
            else:
                search_type = "postcode"

            search_response = search(search_query, search_type)

            if not search_response:
                result = None
            elif search_type == "lpa":
                # For LPA search, we get a single entity result
                result = search_response[0] if search_response else None
            elif search_type == "postcode" and len(search_response) > 2:
                # If there are more than 2 results, choose the item in the middle
                # (user expectation: return the middle item for longer lists).
                mid = len(search_response) // 2
                result = search_response[mid]
            else:
                # Keep existing behaviour for 1 or 2 items (first item)
                result = search_response[0]

            if search_type == "lpa":
                # For LPA, result is the entity with geometry
                name = result.get("name") if result else None
                geometry_data = (
                    result.get("geojson", {}).get("geometry")
                    if result and result.get("geojson")
                    else None
                )

                search_result = {
                    "type": search_type,
                    "query": search_query,
                    "result": result,
                    "geometry": {
                        "name": name,
                        "type": "geometry",
                        "data": geometry_data,
                        "entity": result.get("entity"),
                    }
                    if result and geometry_data
                    else None,
                }
            else:
                # For postcode/UPRN results
                name = (
                    (
                        result.get("POSTCODE")
                        if search_type == "postcode"
                        else result.get("UPRN")
                    )
                    if result
                    else None
                )

                search_result = {
                    "type": search_type,
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
