from geoalchemy2 import Geometry
from sqlalchemy import Column, Date, BIGINT, Text, Index, Integer
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class EntityOrm(Base):

    __tablename__ = "entity"

    entity = Column(BIGINT, primary_key=True, autoincrement=False)
    name = Column(Text, nullable=True)
    entry_date = Column(Date, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    dataset = Column(Text, nullable=True)
    json = Column(JSONB, nullable=True)
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
    EntityOrm.entity,
    EntityOrm.name,
    EntityOrm.entry_date,
    EntityOrm.start_date,
    EntityOrm.end_date,
    EntityOrm.dataset,
    EntityOrm.organisation_entity,
    EntityOrm.prefix,
    EntityOrm.reference,
    EntityOrm.typology,
)


class DatasetOrm(Base):

    __tablename__ = "dataset"

    dataset = Column(Text, primary_key=True)
    name = Column(Text, nullable=True)
    collection = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    entry_date = Column(Date, nullable=True)
    start_date = Column(Text, nullable=True)
    end_date = Column(Date, nullable=True)
    key_field = Column(Text, nullable=True)
    paint_options = Column(JSONB, nullable=True)
    plural = Column(Text, nullable=True)
    prefix = Column(Text, nullable=True)
    text = Column(Text, nullable=True)
    typology = Column(Text, nullable=True)
    wikidata = Column(Text, nullable=True)
    wikipedia = Column(Text, nullable=True)
    themes = Column(ARRAY(Text), nullable=True)


class TypologyOrm(Base):

    __tablename__ = "typology"

    typology = Column(Text, primary_key=True)
    name = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    entry_date = Column(Text, nullable=True)
    start_date = Column(Text, nullable=True)
    end_date = Column(Text, nullable=True)
    plural = Column(Text, nullable=True)
    text = Column(Text, nullable=True)
    wikidata = Column(Text, nullable=True)
    wikipedia = Column(Text, nullable=True)


class OrganisationOrm(Base):

    __tablename__ = "organisation"

    organisation = Column(Text, primary_key=True)
    name = Column(Text, nullable=True)
    combined_authority = Column(Text, nullable=True)
    entry_date = Column(Date, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    entity = Column(BIGINT, nullable=True)
    local_authority_type = Column(Text, nullable=True)
    official_name = Column(Text, nullable=True)
    region = Column(Text, nullable=True)
    statistical_geography = Column(Text, nullable=True)
    website = Column(Text, nullable=True)


class DatasetCollection(Base):

    __tablename__ = "dataset_collection"

    dataset_collection = Column(Text, primary_key=True)
    resource = Column(Text, nullable=True)
    resource_end_date = Column(Date, nullable=True)
    resource_entry_date = Column(Date, nullable=True)
    last_updated = Column(Date, nullable=True)
    last_collection_attempt = Column(Date, nullable=True)


class DatasetPublicationOrm(Base):

    __tablename__ = "dataset_publication"

    dataset_publication = Column(Text, primary_key=True)
    expected_publisher_count = Column(Integer, nullable=False)
    publisher_count = Column(Integer, nullable=False)
