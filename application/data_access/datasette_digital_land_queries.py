import logging

from application.data_access.datasette_query_helpers import get_datasette_http
from application.settings import get_settings


from application.core.models import FieldModel

logger = logging.getLogger(__name__)
settings = get_settings()


def get_field_specifications(fields):
    url = f"{settings.DATASETTE_URL}/digital-land.json"
    sql = f"""
         SELECT
            f.field,
            f.datatype,
            f.name,
            f.typology
         FROM field f
         WHERE field in ('{"','".join(fields)}');
    """

    params = {"sql": sql, "_shape": "array"}

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
