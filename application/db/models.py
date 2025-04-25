import json
from datetime import datetime
from geoalchemy2 import Geometry
from sqlalchemy import Column, Date, BIGINT, Text, Index, Integer, cast, func
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import (
    relationship,
    foreign,
    remote,
    column_property,
)

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
    geometry = Column(Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=True)
    point = Column(Geometry(geometry_type="POINT", srid=4326), nullable=True)
    _geometry_geojson = column_property(func.ST_AsGeoJSON(geometry))
    _point_geojson = column_property(func.ST_AsGeoJSON(point))

    @hybrid_property
    def geojson(self):
        if self._geometry_geojson is not None:
            geometry = json.loads(self._geometry_geojson)
            return {"geometry": geometry, "type": "Feature"}
        elif self._point_geojson is not None:
            geometry = json.loads(self._point_geojson)
            return {"geometry": geometry, "type": "Feature"}
        return None


# Note geoalchemy2 automatically indexes Geometry columns
idx_entity_name = Index("idx_entity_name", EntityOrm.name)
idx_entity_entry_date = Index("idx_entity_entry_date", EntityOrm.entry_date)
idx_entity_start_date = Index("idx_entity_start_date", EntityOrm.start_date)
idx_entity_end_date = Index("idx_entity_end_date", EntityOrm.end_date)
idx_entity_dataset = Index("idx_entity_dataset", EntityOrm.dataset)
idx_entity_organisation_entity = Index(
    "idx_entity_organisation_entity", EntityOrm.organisation_entity
)
idx_entity_prefix = Index("idx_entity_prefix", EntityOrm.prefix)
idx_entity_reference = Index("idx_entity_reference", EntityOrm.reference)
idx_entity_typology = Index("idx_entity_typology", EntityOrm.typology)


class EntitySubdividedOrm(Base):
    __tablename__ = "entity_subdivided"

    entity = Column(BIGINT, primary_key=True, autoincrement=False)
    dataset = Column(Text, nullable=True)
    geometry_subdivided = Column(
        Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=True
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
    dataset = Column(Text, nullable=False)
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
    attribution_id = Column(Text, nullable=True)
    licence_id = Column(Text, nullable=True)
    consideration = Column(Text, nullable=True)
    github_discussion = Column(Integer, nullable=True)
    entity_minimum = Column(BIGINT, nullable=True)
    entity_maximum = Column(BIGINT, nullable=True)
    phase = Column(Text, nullable=True)
    realm = Column(Text, nullable=True)
    replacement_dataset = Column(Text, nullable=True)
    version = Column(Text, nullable=True)

    _attribution = relationship(
        "AttributionOrm",
        foreign_keys=[attribution_id],
        primaryjoin="DatasetOrm.attribution_id == AttributionOrm.attribution",
    )

    _licence = relationship(
        "LicenceOrm",
        foreign_keys=[licence_id],
        primaryjoin="DatasetOrm.licence_id == LicenceOrm.licence",
    )

    @property
    def attribution(self):
        return self._attribution.attribution

    @attribution.setter
    def attribution(self, value):
        self.attribution_id = value

    @property
    def licence(self):
        return self._licence.licence

    @licence.setter
    def licence(self, value):
        self.licence_id = value

    @property
    def attribution_text(self):
        if "[year]" in self._attribution.text:
            current_year = datetime.today().strftime("%Y")
            return self._attribution.text.replace("[year]", current_year)

        return self._attribution.text

    @property
    def licence_text(self):
        if "[year]" in self._licence.text:
            current_year = datetime.today().strftime("%Y")
            return self._licence.text.replace("[year]", current_year)

        return self._licence.text


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


class AttributionOrm(Base):
    __tablename__ = "attribution"

    attribution = Column(Text, primary_key=True)
    text = Column(Text, nullable=True)
    entry_date = Column(Date, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)


class LicenceOrm(Base):
    __tablename__ = "licence"

    licence = Column(Text, primary_key=True)
    text = Column(Text, nullable=True)
    entry_date = Column(Date, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
