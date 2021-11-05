import json
import logging
import urllib

from digital_land.view_model import JSONQueryHelper
from decimal import Decimal
from dl_web.resources import fetch

logger = logging.getLogger(__name__)


# TBD: replace string concatenation with sqlite3 ? expressions ..
def sqlescape(s):
    if s is None:
        return ""
    return s.translate(
        s.maketrans(
            {
                "'": "''",
                '"': "",
                "\\": "",
                "%": "",
                "\0": "",
                "\n": " ",
                "\r": " ",
                "\x08": " ",
                "\x09": " ",
                "\x1a": " ",
            }
        )
    )


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


class EntityJson:
    @staticmethod
    def to_json(data):
        fields = [
            "dataset",
            "entry_date",
            "reference",
            "entity",
            "reference",
            "name",
            "geojson",
            "typology",
        ]
        data_dict = {}
        for key, val in data.items():
            if key in fields:
                val = json.loads(val or "{}") if key == "geojson" else val
                data_dict[key] = val
        return data_dict


def _do_geo_query(longitude: float, latitude: float):
    data = EntityGeoQuery().execute(longitude, latitude)
    results = []
    for row in data.get("rows", []):
        results.append(EntityJson.to_json(row))
    resp = {
        "query": {"longitude": longitude, "latitude": latitude},
        "count": len(results),
        "results": results,
    }
    return resp


class EntityQuery:
    def __init__(
        self, url_base="https://datasette.digital-land.info/entity", params={}
    ):
        self.url_base = url_base
        self.params = params

    async def get_entity(self, **params):
        print(params)
        q = {}
        for key, val in params.items():
            q[f"{key}__exact"] = val
        q = urllib.parse.urlencode(q)
        url = f"{self.url_base}/entity.json?_shape=objects&{q}"
        logger.info(f"get_entity: {url}")
        return await fetch(url)

    def point(self):
        p = self.params
        if p["point"]:
            return p["point"]

        for field in ["longitude", "latitude"]:
            try:
                p[field] = "%.6f" % round(Decimal(p[field]), 6)
            except TypeError:
                return ""

        return "POINT(%s %s)" % (p["longitude"], p["latitude"])

    def geospatial(self):
        point = self.point()
        if not point:
            return ""
        else:
            return """
              entity.entity = geometry.entity
              AND geometry.geometry_geom IS NOT NULL
              AND WITHIN(
                GeomFromText('%s'),
                geometry.geometry_geom
              )
              """ % (
                point
            )

    def sql(self, count=False):
        p = self.params
        if count:
            sql = "SELECT DISTINCT COUNT(*) as _count"
        else:
            sql = "SELECT entity.*, geometry.geojson"

        sql += (
            " FROM entity LEFT OUTER JOIN geometry on entity.entity = geometry.entity"
        )
        where = " WHERE "

        for col in ["typology", "dataset", "entity"]:
            if col in p and p[col]:
                sql += (
                    where
                    + "("
                    + " OR ".join(
                        [
                            "entity.%s = '%s'" % (col, sqlescape(value))
                            for value in p[col]
                        ]
                    )
                    + ")"
                )
                where = " AND "

        geospatial = self.geospatial()
        if geospatial:
            sql += where + geospatial
            where = " AND "

        if p.get("next_entity", ""):
            sql += where + " entity.entity > %s" % (sqlescape(str(p["next_entity"])))

        sql += " ORDER BY entity.entity"
        sql += " LIMIT %s" % (sqlescape(str(p.get("limit", 10))))
        print(sql)
        return sql

    def url(self, sql):
        return JSONQueryHelper.make_url(self.url_base + ".json", params={"sql": sql})

    def response(self, data, count):
        results = []
        for row in data.get("rows", []):
            results.append(EntityJson.to_json(row))

        # remove empty parameters
        params = {k: v for k, v in self.params.items() if v is not None}

        response = {
            "query": params,
            "count": count,
            "results": results,
        }
        return response

    def execute(self):
        count = JSONQueryHelper.get(self.url(self.sql(count=True))).json()["rows"][0][
            "_count"
        ]
        data = JSONQueryHelper.get(self.url(self.sql())).json()
        return self.response(data, count)
