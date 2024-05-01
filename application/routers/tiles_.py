import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

import psycopg2
from io import BytesIO

from application.settings import get_settings

router = APIRouter()
logger = logging.getLogger(__name__)

DATABASE = {"user": "", "password": "", "host": "", "port": "5432", "database": ""}

DATABASE_CONNECTION = None

QUERY_PARAMS = {
    "table1": "entity t1",
    "srid": "4326",
    "geomColumn": "t1.geometry",
    "attrColumns": "t1.entity, t1.name, t1.reference",
}


# ============================================================
# Helper Funcs
# ============================================================
def get_db_connection():
    conn_str = get_settings()

    DATABASE["user"] = conn_str.READ_DATABASE_URL.user
    DATABASE["password"] = conn_str.READ_DATABASE_URL.password
    DATABASE["host"] = conn_str.READ_DATABASE_URL.host
    DATABASE["database"] = conn_str.READ_DATABASE_URL.path.split("/")[1]


get_db_connection()


# Do the tile x/y coordinates make sense at this zoom level?
def tile_is_valid(tile):
    if not ("x" in tile and "y" in tile and "zoom" in tile):
        return False

    if "format" not in tile or tile["format"] not in ["pbf", "mvt"]:
        return False

    size = 2 ** tile["zoom"]

    if tile["x"] >= size or tile["y"] >= size:
        return False

    if tile["x"] < 0 or tile["y"] < 0:
        return False

    return True


def build_db_query(tile):
    qry_params = QUERY_PARAMS.copy()
    qry_params["dataset"] = tile["dataset"]
    qry_params["x"] = tile["x"]
    qry_params["y"] = tile["y"]
    qry_params["z"] = tile["zoom"]

    query = """
    WITH
    webmercator(envelope) AS (
        SELECT ST_TileEnvelope({z}, {x}, {y})
    ),
    wgs84(envelope) AS (
      SELECT ST_Transform((SELECT envelope FROM webmercator), {srid})
    ),
    b(bounds) AS (
      SELECT ST_MakeEnvelope(-180, -85.0511287798066, 180, 85.0511287798066, {srid})
    ),
    geometries(entity, name, reference, wkb_geometry) AS (
        SELECT
            {attrColumns},
            CASE WHEN ST_Covers(b.bounds, {geomColumn})
                 THEN ST_Transform({geomColumn},{srid})
                 ELSE ST_Transform(ST_Intersection(b.bounds, {geomColumn}),{srid})
            END
        FROM
            {table1}
        CROSS JOIN
            b
        WHERE
            {geomColumn} && (SELECT envelope FROM wgs84)
          AND
            t1.dataset = '{dataset}'
    )
    SELECT
        ST_AsMVT(tile, '{dataset}') as mvt
    FROM (
      SELECT
        entity,
        name,
        reference,
        ST_AsMVTGeom(wkb_geometry, (SELECT envelope FROM wgs84))
      FROM geometries
    ) AS tile
    """.format(
        **qry_params
    )

    return query


def sql_to_pbf(sql):
    global DATABASE_CONNECTION

    # Make and hold connection to database
    if not DATABASE_CONNECTION:
        try:
            DATABASE_CONNECTION = psycopg2.connect(**DATABASE)
        except (Exception, psycopg2.Error) as error:
            logger.warning(error)
            return None

    # Query for MVT
    with DATABASE_CONNECTION.cursor() as cur:
        cur.execute(sql)
        if not cur:
            logger.warning(f"sql query failed: {sql}")
            return None

        return cur.fetchone()[0]

    return None


# ============================================================
# API Endpoints
# ============================================================


@router.get("/{dataset}/{z}/{x}/{y}.vector.{fmt}")
async def read_tiles_from_postgres(dataset: str, z: int, x: int, y: int, fmt: str):
    tile = {"dataset": dataset, "zoom": z, "x": x, "y": y, "format": fmt}

    if not tile_is_valid(tile):
        raise HTTPException(status_code=400, detail=f"invalid tile path: {tile}")

    sql = build_db_query(tile)

    pbf = sql_to_pbf(sql)

    pbf_buffer = BytesIO()
    pbf_buffer.write(pbf)
    pbf_buffer.seek(0)

    resp_headers = {
        "Access-Control-Allow-Origin": "*",
        "Content-Type": "application/vnd.mapbox-vector-tile",
    }

    return StreamingResponse(
        pbf_buffer, media_type="vnd.mapbox-vector-tile", headers=resp_headers
    )
