from geoalchemy2 import Geometry
from sqlalchemy import Column, Date, BIGINT, Text, Index
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Entity(Base):

    __tablename__ = "entity"

    entity = Column(BIGINT, primary_key=True, autoincrement=False)
    name = Column(Text, nullable=True)
    entry_date = Column(Date, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    dataset = Column(Text, nullable=True)
    _json = Column("json", JSONB, nullable=True)
    organisation_entity = Column(BIGINT, nullable=True)
    prefix = Column(Text, nullable=True)
    reference = Column(Text, nullable=True)
    typology = Column(Text, nullable=True)
    geojson = Column(JSONB, nullable=True)
    geometry = Column(Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=True)
    point = Column(Geometry(geometry_type="POINT", srid=4326), nullable=True)


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


class Dataset(Base):

    __tablename__ = "dataset"

    dataset = Column(Text, primary_key=True)
    collection = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    end_date = Column(Date, nullable=True)
    entry_date = Column(Date, nullable=True)
    key_field = Column(Text, nullable=True)
    name = Column(Text, nullable=True)
    paint_options = Column(JSONB, nullable=True)
    plural = Column(Text, nullable=True)
    prefix = Column(Text, nullable=True)
    start_date = Column(Text, nullable=True)
    text = Column(Text, nullable=True)
    typology = Column(Text, nullable=True)
    wikidata = Column(Text, nullable=True)
    wikipedia = Column(Text, nullable=True)
    themes = Column(ARRAY(Text), nullable=True)
