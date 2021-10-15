import logging

from fastapi import APIRouter
from starlette.responses import JSONResponse

from dl_web.queries import ViewModelGeoQuery

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/entity", response_class=JSONResponse)
def get_entity_by_long_lat(
    longitude: float,
    latitude: float,
):
    return ViewModelGeoQuery().execute(longitude, latitude)
