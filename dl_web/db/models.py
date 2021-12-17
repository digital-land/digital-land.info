from sqlalchemy import Column, Text, Date, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry

from dl_web.settings import get_settings

sqlalchemy_url = get_settings().DATABASE_URL

Base = declarative_base()


# this is a test module to experiment with using postgis via sqlalchemy and geoalchemy2
# in this application - it should be removed if/when we move the code over to using it
# and potentially much different model classes.


class Entity(Base):

    __tablename__ = "entity"

    entity = Column(Integer, primary_key=True)
    name = Column(Text)
    entry_date = Column(Date)
    start_date = Column(Date)
    end_date = Column(Date)
    dataset = Column(Text)
    _json = Column("json", JSONB)
    organisation_entity = Column(Integer)
    prefix = Column(Text)
    reference = Column(Text)
    typology = Column(Text)
    geojson = Column(JSONB)
    geometry = Column(Geometry(geometry_type="MULTIPOLYGON", srid=4326))
    point = Column(Geometry(geometry_type="POINT", srid=4326))
