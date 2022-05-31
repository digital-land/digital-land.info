from geoalchemy2 import Geometry
from sqlalchemy import Column, Date, BIGINT, Text, Index, Integer, cast
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, foreign, remote

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


class OldEntityOrm(Base):

    __tablename__ = "old_entity"

    old_entity_id = Column(
        BIGINT, name="old_entity", primary_key=True, autoincrement=False
    )
    old_entity = relationship(
        EntityOrm,
        primaryjoin=remote(EntityOrm.entity) == cast(foreign(old_entity_id), Integer),
        backref="new_entity_mapping",
        uselist=False,
    )
    entry_date = Column(Date, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    status = Column(Integer, nullable=False)
    notes = Column(Text, nullable=True)
    new_entity_id = Column(BIGINT, name="entity", nullable=True)
    new_entity = relationship(
        EntityOrm,
        primaryjoin=remote(EntityOrm.entity) == foreign(new_entity_id),
        backref="old_entity_mappings",
        uselist=False,
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

    def type(self):
        return self.organisation.split(":")[0]


class DatasetCollectionOrm(Base):

    __tablename__ = "dataset_collection"

    dataset_collection = Column(Text, primary_key=True)
    resource = Column(Text, nullable=True)
    resource_end_date = Column(Date, nullable=True)
    resource_entry_date = Column(Date, nullable=True)
    last_updated = Column(Date, nullable=True)
    last_collection_attempt = Column(Date, nullable=True)


class DatasetPublicationCountOrm(Base):

    __tablename__ = "dataset_publication"

    dataset_publication = Column(Text, primary_key=True)
    expected_publisher_count = Column(Integer, nullable=False)
    publisher_count = Column(Integer, nullable=False)


class LookupOrm(Base):

    __tablename__ = "lookup"

    id = Column(BIGINT, primary_key=True, autoincrement=False)
    entity = Column(BIGINT)
    entry_number = Column(BIGINT)
    prefix = Column(Text, nullable=True)
    reference = Column(Text, nullable=True)
    value = Column(Text, nullable=True)
    entry_date = Column(Date, nullable=True)
    start_date = Column(Date, nullable=True)


class FactOrm(Base):

    __tablename__ = "fact"

    fact = Column(Text, primary_key=True)
    entity = Column(BIGINT, nullable=False)
    field = Column(Text, nullable=True)
    value = Column(Text, nullable=True)
    reference_entity = Column(BIGINT, nullable=True)
    entry_date = Column(Date, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)


Index("idx_fact_entity", FactOrm.entity)
