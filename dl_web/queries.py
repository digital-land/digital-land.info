import logging
import urllib

from digital_land.view_model import JSONQueryHelper

from dl_web.resources import fetch

logger = logging.getLogger(__name__)


class EntityGeoQuery:
    def __init__(self, url_base="https://datasette.digital-land.info/entity"):
        self.url_base = url_base

    def execute(self, longitude, latitude):
        sql = f"""
            SELECT
              e.*,
              g.geojson
            FROM
              entity e,
              geometry g
            WHERE
              e.entity = g.entity
              and g.geometry_geom IS NOT NULL
              and WITHIN(
                GeomFromText('POINT({longitude} {latitude})'),
                g.geometry_geom
              )
            ORDER BY
              e.entity
      """
        query_url = JSONQueryHelper.make_url(
            f"{self.url_base}.json", params={"sql": sql}
        )
        return JSONQueryHelper.get(query_url).json()


class EntityQuery:
    def __init__(self, url_base="https://datasette.digital-land.info/entity"):
        self.url_base = url_base

    async def get_entity(self, **params):
        q = {}
        for key, val in params.items():
            q[f"{key}__exact"] = val
        q = urllib.parse.urlencode(q)
        url = f"{self.url_base}/entity.json?_shape=objects&{q}"
        logger.info(f"get_entity: {url}")
        return await fetch(url)
