from datetime import date
from typing import Optional, List, Dict

from geoalchemy2.shape import to_shape
from pydantic import BaseModel, Field, validator, Extra

from application.db.models import EntityOrm


def to_kebab(string: str) -> str:
    return string.replace("_", "-")


class GeoJSON(BaseModel):
    geometry: dict
    type: str = "Feature"
    properties: dict = None


class GeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[GeoJSON]


class DigitalLandBaseModel(BaseModel):
    class Config:
        alias_generator = to_kebab
        allow_population_by_field_name = True
        orm_mode = True
        arbitrary_types_allowed = True


class DigitalLandDateFieldsModel(DigitalLandBaseModel):
    entry_date: Optional[date] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


def _make_geometry(v, values) -> str:
    if v is not None:
        s = to_shape(v)
        return s.wkt


class EntityModel(DigitalLandDateFieldsModel, extra=Extra.allow):
    entity: int = None
    name: str = None
    dataset: str = None
    typology: str = None
    reference: str = None
    prefix: str = None
    organisation_entity: str = None
    geojson: GeoJSON = None
    geometry: str = None
    point: str = None

    _validate_geometry = validator("geometry", pre=True, always=True, allow_reuse=True)(
        _make_geometry
    )
    _validate_point = validator("point", pre=True, always=True, allow_reuse=True)(
        _make_geometry
    )


class DatasetModel(DigitalLandDateFieldsModel):
    collection: str = None
    dataset: str = None
    description: str = None
    name: str = None
    plural: str = None
    prefix: str = None
    text: str = None
    typology: str = None
    wikidata: str = None
    wikipedia: str = None
    entities: Optional[List[EntityModel]]
    themes: Optional[List[str]]
    entity_count: int = None
    paint_options: dict = Field(None)


class TypologyModel(DigitalLandDateFieldsModel):
    typology: str = None
    name: str = None
    description: str = None
    plural: str = None
    text: str = None
    wikidata: str = None
    wikipedia: str = None


class OrganisationModel(DigitalLandDateFieldsModel):
    organisation: str = None
    name: str = None
    combined_authority: str = None
    entity: int = None
    local_authority_type: str = None
    official_name: str = None
    region: str = None
    statistical_geography: str = None
    website: str = None


class OrganisationsByTypeModel(BaseModel):
    organisations: Dict[str, List[OrganisationModel]]


class DatasetCollectionModel(DigitalLandBaseModel):
    dataset_collection: str = None
    resource: str = None
    resource_end_date: Optional[date] = None
    resource_entry_date: Optional[date] = None
    last_updated: Optional[date] = None
    last_collection_attempt: Optional[date] = None


class DatasetPublicationCountModel(DigitalLandBaseModel):
    dataset_publication: str
    expected_publisher_count: int
    publisher_count: int


def entity_factory(entity_orm: EntityOrm):
    e = EntityModel.from_orm(entity_orm)
    if entity_orm.json is not None:
        for key, val in entity_orm.json.items():
            setattr(e, key, val)
    return e


class FactModel(DigitalLandBaseModel):
    fact: str
    entity: int
    reference_entity: Optional[int] = None
    field: str
    value: str
    entity_name: Optional[str] = None
    entity_prefix: Optional[str] = None
    entity_reference: Optional[str] = None
    earliest_entry_date: Optional[date] = None
    latest_entry_date: Optional[date] = None
    latest_resource: Optional[str] = None
    resources: Optional[str] = None


class DatasetFieldModel(DigitalLandBaseModel):
    field: str
    # dataset: str
    # entry_date: Optional[date] = None
    # start_date: Optional[date] = None
    # end_date: Optional[date] = None
