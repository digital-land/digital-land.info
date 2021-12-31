import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from application.db.models import Entity as EntityModel
from application.core.models import Entity
from application.db.session import get_db_session

router = APIRouter()
logger = logging.getLogger(__name__)

# this is a test module to experiment with using postgis via sqlalchemy and geoalchemy2
# in this application - it should be removed if/when we move the code over to using it
# and potentially much different model classes.


def get_entities(db_session: Session = Depends(get_db_session)):
    try:
        entities = db_session.query(EntityModel).limit(50).all()
        return {"entities": [Entity.from_orm(e) for e in entities]}
    except Exception as e:
        print(e)
        return []


router.add_api_route("/entities", endpoint=get_entities, response_class=JSONResponse)
