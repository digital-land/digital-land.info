import logging

from fastapi import APIRouter
from sqlalchemy.orm import Session

from application.db.models import LookupOrm, EntityOrm


router = APIRouter()
logger = logging.getLogger(__name__)


def get_lookup_by_curie(session: Session, prefix: str, reference: str):
    """
    This function queries the database for lookup records matching the given
    prefix and reference components of a CURIE. It limits results to 2 records
    and logs a warning if duplicates are found.

    Args:
        session (Session): SQLAlchemy database session for executing the query
        prefix (str): The prefix component of the CURIE
        reference (str): The reference component of the CURIE
    Returns:
        list: A list of lookup IDs matching the given CURIE prefix
              and reference. May contain up to 2 results.
    """
    statement = (
        session.query(LookupOrm.entity.label("entity"))
        .filter(LookupOrm.prefix == prefix, LookupOrm.reference == reference)
        .limit(2)
    )
    lookup_ids = session.execute(statement).scalars().all()

    if len(lookup_ids) > 1:
        logger.info(f"Lookup with CURIE {repr(f'{prefix}:{reference}')} is a duplicate")

    return lookup_ids


def get_entity_by_curie(session: Session, prefix: str, reference: str):
    """
    This function queries the database for entity records matching the given
    prefix and reference components of a CURIE. It limits results to 2 records
    and logs a warning if duplicates are found.

    Args:
        session (Session): SQLAlchemy database session for executing the query
        prefix (str): The prefix component of the CURIE
        reference (str): The reference component of the CURIE
    Returns:
        list: A list of entity IDs matching the given CURIE prefix
              and reference. May contain up to 2 results.
    """
    # To check if there are any duplicate entities we just need to
    # see if 2 rows exist, so we `limit` to 2
    statement = (
        session.query(EntityOrm.entity.label("entity"))
        .filter(EntityOrm.prefix == prefix, EntityOrm.reference == reference)
        .limit(2)
    )
    entity_ids = session.execute(statement).scalars().all()

    if len(entity_ids) > 1:
        logger.info(f"Entity with CURIE {repr(f'{prefix}:{reference}')} is a duplicate")

    return entity_ids
