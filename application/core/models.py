from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field

from application.db.models import EntityOrm


def to_kebab(string: str) -> str:
    return string.replace("_", "-")


class GeoJSON(BaseModel):
    geometry: dict
    type: str = "Feature"
    properties: dict = None


class GeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureColletion"
    features: List[GeoJSON]


class DigitalLandBaseModel(BaseModel):
    entry_date: Optional[date] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    class Config:
        alias_generator = to_kebab
        allow_population_by_field_name = True
        orm_mode = True


class EntityModel(DigitalLandBaseModel):
    entity: int = None
    name: str = None
    dataset: str = None
    typology: str = None
    reference: str = None
    prefix: str = None
    organisation_entity: str = None
    geojson: GeoJSON = None
    json_: dict = Field(None, alias="json")


class DatasetModel(DigitalLandBaseModel):
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


class TypologyModel(DigitalLandBaseModel):
    typology: str = None
    name: str = None
    description: str = None
    plural: str = None
    text: str = None
    wikidata: str = None
    wikipedia: str = None


class OrganisationModel(DigitalLandBaseModel):
    organisation: str = None
    name: str = None
    combined_authority: str = None
    entity: int = None
    local_authority_type: str = None
    official_name: str = None
    region: str = None
    statistical_geography: str = None
    website: str = None


def entity_factory(entity_orm: EntityOrm):
    e = EntityModel.from_orm(entity_orm)
    if e.geojson is not None:
        e.geojson.properties = e.dict(exclude={"geojson"}, by_alias=True)
    return e
