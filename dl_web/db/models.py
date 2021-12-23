from geoalchemy2 import Geometry
from sqlalchemy import Column, Date, BIGINT, Text, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Entity(Base):

    __tablename__ = "entity"

    entity = Column(BIGINT, primary_key=True, autoincrement=False)
    name = Column(Text)
    entry_date = Column(Date)
    start_date = Column(Date)
    end_date = Column(Date)
    dataset = Column(Text)
    _json = Column("json", JSONB)
    organisation_entity = Column(BIGINT)
    prefix = Column(Text)
    reference = Column(Text)
    typology = Column(Text)
    geojson = Column(JSONB)
    geometry = Column(Geometry(geometry_type="MULTIPOLYGON", srid=4326))
    point = Column(Geometry(geometry_type="POINT", srid=4326))


# Note geoalchemy2 automatically indexes Geometry columns
idx_entity_columns = Index(
    "idx_entity_columns",
    Entity.entity,
    Entity.name,
    Entity.entry_date,
    Entity.start_date,
    Entity.end_date,
    Entity.dataset,
    Entity.organisation_entity,
    Entity.prefix,
    Entity.reference,
    Entity.typology,
)
