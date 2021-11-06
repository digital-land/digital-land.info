import logging

from digital_land.entity_lookup import lookup_by_slug
from digital_land.view_model import ViewModel
from fastapi import HTTPException

logger = logging.getLogger(__name__)


def fetch_entity_metadata(
    view_model: ViewModel,
    entity: int,
) -> dict:
    metadata = view_model.get_entity_metadata(entity)
    if not metadata:
        raise HTTPException(status_code=404, detail="entity not found")
    return metadata


def fetch_entity(
    view_model: ViewModel,
    entity: int,
    entity_metadata: dict,
) -> dict:
    try:
        entity_snapshot = view_model.get_entity(entity_metadata["typology"], entity)
    except (AssertionError, KeyError):
        entity_snapshot = None

    if not entity_snapshot:
        raise HTTPException(status_code=404, detail="entity not found")

    entity_snapshot = {
        k.replace("_", "-"): v
        for k, v in entity_snapshot.items()
        if v and k not in ("geometry")
    }

    return entity_snapshot


def lookup_entity(slug: str) -> int:
    try:
        entity = lookup_by_slug(slug)
    except ValueError as err:
        logger.warning("lookup_by_slug failed: %s", err)
        raise HTTPException(status_code=404, detail="slug lookup failed")

    return entity
