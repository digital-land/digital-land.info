import json
import logging

from decimal import Decimal
from typing import Optional, List

from sqlalchemy import func

from application.core.models import entity_factory
from application.core.models import EntityModel
from application.db.models import EntityOrm
from application.core.utils import make_url, get
from application.search.enum import EntriesOption, DateOption, GeometryRelation
from application.settings import get_settings
from application.db.session import get_context_session

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


class EntityQuery:
    lists = [
        "typology",
        "dataset",
        "entity",
        "prefix",
        "reference",
        "organisation_entity",
    ]

    def __init__(self, params: dict = {}):
        datasette_url = get_settings().DATASETTE_URL
        self.url_base = f"{datasette_url}/entity"
        self.params = self.normalised_params(params)

    def normalised_params(self, params):
        # remove empty parameters
        params = {k: v for k, v in params.items() if v}

        # sort/unique list parameters
        for lst in self.lists:
            if lst in params:
                # remove empty list parameters
                params[lst] = [v for v in params[lst] if v]
                params[lst] = sorted(set(params[lst]))

        return params

    def where_column(self, params):
        sql = where = ""
        for col in [
            "typology",
            "dataset",
            "entity",
            "prefix",
            "reference",
            "organisation_entity",
        ]:
            if col in params and params[col]:
                sql += (
                    where
                    + "("
                    + " OR ".join(
                        [
                            "entity.%s = '%s'" % (col, sqlescape(value))
                            for value in params[col]
                        ]
                    )
                    + ")"
                )
                where = " AND "
        return sql

    def where_organisation(self, params):
        sql = where = ""
        if "organisation" in params and params["organisation"]:
            sql += (
                where
                + "("
                + " OR ".join(
                    [
                        "(entity.organisation_entity = (SELECT entity from entity "
                        + "where entity.prefix = '{c[0]}' and entity.reference = '{c[1]}' group by entity))".format(
                            c=[sqlescape(s) for s in c.split(":") + ["", ""]]
                        )
                        for c in params["organisation"]
                    ]
                )
                + ")"
            )
        return sql

    def where_curie(self, params):
        sql = where = ""
        if "curie" in params and params["curie"]:
            sql += (
                where
                + "("
                + " OR ".join(
                    [
                        "(entity.prefix = '{c[0]}' AND entity.reference = '{c[1]}')".format(
                            c=[sqlescape(s) for s in c.split(":") + ["", ""]]
                        )
                        for c in params["curie"]
                    ]
                )
                + ")"
            )
        return sql

    def where_entries(self, params):
        option = params.get("entries", EntriesOption.all)
        if option == EntriesOption.current:
            return " entity.end_date is ''"
        if option == EntriesOption.historical:
            return " entity.end_date is not ''"

    def get_date(self, params, param):
        if param in params:
            d = params[param]
            params[param + "_year"] = d.year
            params[param + "_month"] = d.month
            params[param + "_day"] = d.day
            return d.isoformat()

        try:
            year = int(params.get(param + "_year", 0))
            if year:
                month = int(params.setdefault(param + "_month", 1))
                day = int(params.setdefault(param + "_day", 1))
                return "%04d-%02d-%02d" % (year, month, day)
        except ValueError:
            return

    def where_date(self, params):
        sql = where = ""
        for col in ["start_date", "end_date", "entry_date"]:
            param = "entry_" + col
            value = self.get_date(params, param)
            match = params.get(param + "_match", "")
            if match:
                if match == DateOption.empty:
                    sql += where + " entity.%s = ''" % col
                    where = " AND "
                elif value:
                    operator = {
                        DateOption.match: "=",
                        DateOption.before: "<",
                        DateOption.since: ">=",
                    }[match]
                    sql += where + "(entity.%s != '' AND entity.%s %s '%s') " % (
                        col,
                        col,
                        operator,
                        sqlescape(value),
                    )
                    where = " AND "
        return sql

    # a single point maybe provided as longitude and latitude params
    def get_point(self, params):
        for field in ["longitude", "latitude"]:
            try:
                params[field] = "%.6f" % round(Decimal(params[field]), 6)
            except (KeyError, TypeError):
                return

        return "POINT(%s %s)" % (params["longitude"], params["latitude"])

    def where_geometry(self, params):
        values = []

        point = self.get_point(params)
        if point:
            values.append("GeomFromText('%s')" % sqlescape(point))

        for geometry in params.get("geometry", []):
            values.append("GeomFromText('%s')" % sqlescape(geometry))

        for entity in params.get("geometry_entity", []):
            values.append(
                "(SELECT geometry_geom from entity where entity = '%s')"
                % sqlescape(entity)
            )

        for reference in params.get("geometry_reference", []):
            values.append(
                """
                  (SELECT geometry_geom from entity where entity =
                      (SELECT entity from entity where reference = '%s' group by entity))
                """
                % sqlescape(reference)
            )

        if not values:
            return

        sql = ""
        where = " ("
        match = params.get("geometry_relation", GeometryRelation.intersects).value
        for value in values:
            sql += where + "(geometry_geom IS NOT NULL AND %s(geometry_geom, %s))" % (
                match,
                value,
            )
            where = " OR "
            sql += where + "%s(point_geom, %s)" % (match, value)
        return sql + ")"

    def pagination(self, where, params):
        sql = ""
        if params.get("next_entity", ""):
            sql += where + " entity.entity > %s" % (
                sqlescape(str(params["next_entity"]))
            )
        sql += " ORDER BY entity.entity"
        sql += " LIMIT %s" % (sqlescape(str(params.get("limit", 10))))
        return sql

    def sql(self, count=False):
        if count:
            sql = "SELECT DISTINCT COUNT(*) as _count"
        else:
            sql = "SELECT entity.* "
        sql += " FROM entity "

        where = " WHERE "
        for part in [
            "column",
            "organisation",
            "curie",
            "entries",
            "date",
            "geometry",
        ]:
            clause = getattr(self, "where_" + part)(self.params)
            if clause:
                sql += where + clause
                where = " AND "

        sql += self.pagination(where, self.params)

        print(sql)
        return sql

    def url(self, sql):
        return make_url(self.url_base + ".json", params={"sql": sql})

    def response(self, data, count):
        results = []
        for row in data.get("rows", []):
            # TODO see if there's a way to handle this conversion of string
            # geojson to json in pydantic
            for key, val in row.items():
                if key == "geojson" and row.get("geojson"):
                    row["geojson"] = json.loads(row["geojson"])
                if isinstance(val, str) and not val:
                    row[key] = None
            results.append(entity_factory(row))

        response = {
            "query": self.params,
            "count": count,
            "results": results,
        }
        return response

    def execute(self):
        r = get(self.url(self.sql(count=True))).json()
        if "rows" not in r or not len(r["rows"]):
            count = 0
        else:
            count = r["rows"][0]["_count"]
        data = get(self.url(self.sql())).json()
        return self.response(data, count)


def normalised_params(params):
    lists = [
        "typology",
        "dataset",
        "entity",
        "prefix",
        "reference",
        "organisation_entity",
    ]

    params = {k: v for k, v in params.items() if v}

    for lst in lists:
        if lst in params:
            params[lst] = [v for v in params[lst] if v]
            params[lst] = sorted(set(params[lst]))

    return params


def get_entity_query(id: int):
    with get_context_session() as session:
        entity = session.query(EntityOrm).get(id)
        if entity is not None:
            return EntityModel.from_orm(entity)
        else:
            return None


def get_entity_count(dataset: Optional[str] = None):

    from sqlalchemy import select
    from sqlalchemy import func

    sql = select(EntityOrm.dataset, func.count(func.distinct(EntityOrm.entity)))
    sql = sql.group_by(EntityOrm.dataset)
    if dataset is not None:
        sql = sql.filter(EntityOrm.dataset == dataset)
    with get_context_session() as session:
        result = session.execute(sql)
        if dataset is not None:
            return result.fetchone()
        else:
            return result.fetchall()


def get_entities(dataset: str, limit: int) -> List[EntityOrm]:
    with get_context_session() as session:
        entities = (
            session.query(EntityOrm)
            .filter(EntityOrm.dataset == dataset)
            .limit(limit)
            .all()
        )
        return [EntityModel.from_orm(e) for e in entities]


def entity_search(params: dict):
    with get_context_session() as session:
        query = session.query(
            EntityOrm, func.count(EntityOrm.entity).over().label("count_all")
        )

        for key, val in params.items():
            if hasattr(EntityOrm, key):
                field = getattr(EntityOrm, key)
                if isinstance(val, list):
                    query = query.filter(field.in_(val))
                else:
                    query = query.filter(field == val)

        query = query.order_by(EntityOrm.entity).limit(params["limit"])

        if params.get("offset") is not None:
            query = query.offset(params["offset"])

        entities = query.all()

        if entities:
            count_all = entities[0].count_all
        else:
            count_all = 0

        return {
            "count_all": count_all,
            "entities": [EntityModel.from_orm(e.EntityOrm) for e in entities],
        }
