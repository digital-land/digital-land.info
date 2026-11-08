import logging

from application.data_access.datasette_query_helpers import get_datasette_http
from application.settings import get_settings


from application.core.models import FieldModel

logger = logging.getLogger(__name__)


def get_field_specifications(fields):
    url = f"{get_settings().DATASETTE_URL}/digital-land.json"
    # Bind field values as datasette named parameters rather than
    # interpolating them into the SQL, to prevent SQL injection.
    field_params = {f"field{i}": value for i, value in enumerate(fields)}
    placeholders = ", ".join(f":{name}" for name in field_params) or "NULL"
    sql = f"""
         SELECT
            f.field,
            f.datatype,
            f.name,
            f.typology,
            f.uri_template
         FROM field f
         WHERE field in ({placeholders});
    """

    params = {"sql": sql, "_shape": "array", **field_params}

    try:
        http = get_datasette_http()
        resp = http.get(url, params=params)
        resp.raise_for_status()
        rows = resp.json()
        # datasette returns empty strings for nulls. is there
        # a datasette config way to prevent this? for now set empties
        # to None.
        for r in rows:
            for key, val in r.items():
                if not val:
                    r[key] = None
        fields = [FieldModel(**field) for field in rows]
        return fields
    except Exception as e:
        logger.warning(e)
        return None
