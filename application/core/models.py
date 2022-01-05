from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field, Json


def to_kebab(string: str) -> str:
    return string.replace("_", "-")


class GeoJSON(BaseModel):
    geometry: dict
    type: str = "Feature"
    properties: dict = None


class GeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureColletion"
    features: List[GeoJSON]


class DigitalLandBase(BaseModel):
    entry_date: Optional[date] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    class Config:
        alias_generator = to_kebab
        allow_population_by_field_name = True
        orm_mode = True


class Entity(DigitalLandBase):
    entity: str = None
    name: str = None
    dataset: str = None
    typology: str = None
    reference: str = None
    prefix: str = None
    organisation_entity: str = None
    geojson: GeoJSON = None
    json_: Json = Field(None, alias="json")


class Dataset(DigitalLandBase):
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
    entities: Optional[List[Entity]]


def entity_factory(data):
    e = Entity(**data)
    if e.geojson is not None:
        e.geojson.properties = e.dict(exclude={"geojson"}, by_alias=True)
    return e
