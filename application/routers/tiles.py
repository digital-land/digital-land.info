from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, case, and_
from io import BytesIO

from application.db.models import EntityOrm
from application.db.session import get_session

router = APIRouter()

# ============================================================
# Helper Funcs
# ============================================================


# Validate tile x/y coordinates at the given zoom level
def tile_is_valid(tile):
    size = 2 ** tile["zoom"]
    return (
        0 <= tile["x"] < size
        and 0 <= tile["y"] < size
        and tile["format"] in ["pbf", "mvt"]
    )


# Build the database query using SQLAlchemy ORM to match the direct SQL logic
def build_db_query(tile, session: Session):
    srid = 4326  # WGS 84

    # Define the envelope, webmercator, and WGS84 transformations
    envelope = func.ST_TileEnvelope(tile["zoom"], tile["x"], tile["y"])
    webmercator = envelope
    wgs84 = func.ST_Transform(webmercator, srid)
    bounds = func.ST_MakeEnvelope(-180, -85.0511287798066, 180, 85.0511287798066, srid)

    # Define the CASE expression for geometry transformation
    geometry_case = case(
        [
            (
                func.ST_Covers(bounds, EntityOrm.geometry),
                func.ST_Transform(EntityOrm.geometry, srid),
            )
        ],
        else_=func.ST_Transform(func.ST_Intersection(bounds, EntityOrm.geometry), srid),
    )

    # Geometry processing for MVT
    query = (
        session.query(func.ST_AsMVTGeom(geometry_case, wgs84).label("geom"))
        .filter(
            and_(
                func.ST_Intersects(EntityOrm.geometry, wgs84),
                EntityOrm.dataset == tile["dataset"],
            )
        )
        .subquery()
    )

    # Generate MVT from a single-column subquery
    tile_data = session.query(func.ST_AsMVT(query.c.geom, tile["dataset"])).scalar()

    return tile_data


# ============================================================
# API Endpoints
# ============================================================


@router.get("/{dataset}/{z}/{x}/{y}.vector.{fmt}")
async def read_tiles_from_postgres(
    request: Request,
    dataset: str,
    z: int,
    x: int,
    y: int,
    fmt: str,
    session: Session = Depends(get_session),
):
    print("Hello", {dataset})
    tile = {"dataset": dataset, "zoom": z, "x": x, "y": y, "format": fmt}
    if not tile_is_valid(tile):
        raise HTTPException(status_code=400, detail=f"Invalid tile path: {tile}")

    tile_data = build_db_query(tile, session)
    if not tile_data:
        raise HTTPException(status_code=404, detail="Tile data not found")

    pbf_buffer = BytesIO(tile_data)
    resp_headers = {
        "Access-Control-Allow-Origin": "*",
        "Content-Type": "application/vnd.mapbox-vector-tile",
    }

    return StreamingResponse(
        pbf_buffer, media_type="vnd.mapbox-vector-tile", headers=resp_headers
    )
