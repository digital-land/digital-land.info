import json
from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field


def to_kebab(string: str) -> str:
    return string.replace("_", "-")


class GeoJSON(BaseModel):
    geometry: dict
    type: str = "Feature"
    properties: dict = None


class DigitalLandBase(BaseModel):
    entry_date: Optional[date] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

    class Config:
        alias_generator = to_kebab
        allow_population_by_field_name = True


class Entity(DigitalLandBase):
    entity: str = None
    name: str = None
    dataset: str = None
    typology: str = None
    reference: str = None
    prefix: str = None
    organisation_entity: str = None
    geojson: GeoJSON = None
    json_: dict = Field(None, alias="json")


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

    # a bit hacky but json in data is stringified. Need to work out how to tell
    # pydantic to just take care of it and not had to json.loads it manually
    if "json" in data.keys():
        json_blob = data.pop("json")

    e = Entity(**data)

    if json_blob:
        e.json_ = json.loads(json_blob)

    if e.geojson is not None:
        e.geojson.properties = e.dict(exclude={"geojson"}, by_alias=True)

    return e
