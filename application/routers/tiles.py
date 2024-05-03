import logging
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from io import BytesIO

from application.db.models import EntityOrm
from application.db.session import get_session

router = APIRouter()
logger = logging.getLogger(__name__)

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


# Build the database query using SQLAlchemy ORM
def build_db_query(tile, session: Session):
    envelope = func.ST_TileEnvelope(tile["zoom"], tile["x"], tile["y"])

    geometries = (
        session.query(
            EntityOrm.entity,
            EntityOrm.name,
            EntityOrm.reference,
            func.ST_AsMVTGeom(EntityOrm.geometry, envelope),
        )
        .filter(
            EntityOrm.dataset == tile["dataset"],
            EntityOrm.geometry.ST_Intersects(envelope),
        )
        .subquery()
    )

    # Build vector tile
    tile_data = session.query(func.ST_AsMVT(geometries, tile["dataset"])).scalar()

    return tile_data


# ============================================================
# API Endpoints
# ============================================================


@router.get("/tiles/{dataset}/{z}/{x}/{y}.{fmt}")
async def read_tiles_from_postgres(
    dataset: str,
    z: int,
    x: int,
    y: int,
    fmt: str,
    session: Session = Depends(get_session),
):
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
