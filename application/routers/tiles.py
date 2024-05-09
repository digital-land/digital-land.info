from fastapi import APIRouter, HTTPException, Depends, Response
from sqlalchemy.orm import Session
import math
from sqlalchemy import text
from application.db.session import get_session

router = APIRouter()


def tile_is_valid(z, x, y, fmt):
    max_tile = 2**z - 1
    return 0 <= x <= max_tile and 0 <= y <= max_tile and fmt in ["pbf", "mvt"]


def tile_bounds(z, x, y):
    n = 2.0**z
    lon_min = x / n * 360.0 - 180.0
    lat_min = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))
    lon_max = (x + 1) / n * 360.0 - 180.0
    lat_max = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * (y + 1) / n))))
    return lon_min, lat_min, lon_max, lat_max


def build_db_query(tile, session: Session):
    z, x, y, dataset = tile["zoom"], tile["x"], tile["y"], tile["dataset"]
    lon_min, lat_min, lon_max, lat_max = tile_bounds(z, x, y)

    geometry_column = "geometry"
    if dataset == "conservation-area":
        geometry_column = "point"

    tile_width = 256

    mvt_geom_query = text(
        f"""
        SELECT ST_AsMVT(q, 'entities_layer', {tile_width}, 'geom') AS mvt
        FROM (
            SELECT ST_AsMVTGeom(
                {geometry_column},
                ST_MakeEnvelope(:lon_min, :lat_min, :lon_max, :lat_max, 4326),
                {tile_width}, 4096, true) AS geom
            FROM entity
            WHERE dataset = :dataset
              AND ST_Intersects({geometry_column}, ST_MakeEnvelope(:lon_min, :lat_min, :lon_max, :lat_max, 4326))
        ) AS q
    """
    )

    result = session.execute(
        mvt_geom_query,
        {
            "lon_min": lon_min,
            "lat_min": lat_min,
            "lon_max": lon_max,
            "lat_max": lat_max,
            "dataset": dataset,
        },
    ).scalar()
    return result


@router.get("/{dataset}/{z}/{x}/{y}.vector.{fmt}")
async def read_tiles(
    dataset: str,
    z: int,
    x: int,
    y: int,
    fmt: str,
    session: Session = Depends(get_session),
):
    if not tile_is_valid(z, x, y, fmt):
        raise HTTPException(status_code=400, detail="Invalid tile path")

    tile = {"dataset": dataset, "zoom": z, "x": x, "y": y, "format": fmt}
    mvt_data = build_db_query(tile, session)
    if not mvt_data:
        raise HTTPException(status_code=404, detail="Tile data not found")

    return Response(
        content=mvt_data.tobytes(), media_type="application/vnd.mapbox-vector-tile"
    )
