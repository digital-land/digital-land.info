from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from application.db.models import EntityOrm
from application.db.session import get_session

router = APIRouter()


def tile_is_valid(z, x, y, fmt):
    max_tile = 2**z - 1
    return 0 <= x <= max_tile and 0 <= y <= max_tile and fmt in ["pbf", "mvt"]


def build_db_query(tile, session: Session):
    # z, x, y, dataset = tile["zoom"], tile["x"], tile["y"], tile["dataset"]
    dataset = tile["dataset"]
    geometries = session.query(EntityOrm).filter(EntityOrm.dataset == dataset).all()
    return geometries


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
    geometries = build_db_query(tile, session)
    if not geometries:
        raise HTTPException(status_code=404, detail="Tile data not found")

    geojson_features = [
        {"type": "Feature", "geometry": geom.geojson} for geom in geometries
    ]

    geojson_data = {"type": "FeatureCollection", "features": geojson_features}

    return geojson_data
