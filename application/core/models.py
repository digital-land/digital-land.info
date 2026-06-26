from datetime import date
from typing import Optional, List, Dict, Any

from geoalchemy2.shape import to_shape
from geoalchemy2.elements import WKBElement, WKTElement
from pydantic import BaseModel, Field, field_validator, create_model

from application.db.models import EntityOrm
from application.core.utils import to_snake


def to_kebab(string: str) -> str:
    return string.replace("_", "-")


class GeoJSON(BaseModel):
    geometry: dict
    type: str = "Feature"
    properties: Optional[dict] = None


class GeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[GeoJSON]


class DigitalLandBaseModel(BaseModel):
    class Config:
        alias_generator = to_kebab
        populate_by_name = True
        from_attributes = True
        arbitrary_types_allowed = True


class DigitalLandDateFieldsModel(DigitalLandBaseModel):
    entry_date: Optional[date] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


# cannot currently accept raw strings for geometry and
def _make_geometry(v) -> str:
    """
    A function to allow for conversaion from other
    spatial types into a WKT (i.e. a string) before
    pydantic validation occurs
    """
    if v is not None and type(v) in [WKBElement, WKTElement]:
        s = to_shape(v)
        return s.wkt
    else:
        return v


class EntityModel(DigitalLandDateFieldsModel):
    model_config = {"extra": "allow"}
    entity: Optional[int] = None
    name: Optional[str] = None
    dataset: Optional[str] = None
    typology: Optional[str] = None
    reference: Optional[str] = None
    prefix: Optional[str] = None
    organisation_entity: Optional[int] = None
    geojson: Optional[GeoJSON] = None
    geometry: Optional[str] = None
    point: Optional[str] = None
    quality: Optional[str] = None

    @field_validator("geometry", "point", mode="before")
    @classmethod
    def _validate_geometry_fields(cls, v):
        return _make_geometry(v)


class DatasetModel(DigitalLandDateFieldsModel):
    collection: Optional[str] = None
    dataset: Optional[str] = None
    description: Optional[str] = None
    name: Optional[str] = None
    plural: Optional[str] = None
    prefix: Optional[str] = None
    text: Optional[str] = None
    typology: Optional[str] = None
    wikidata: Optional[str] = None
    wikipedia: Optional[str] = None
    entities: Optional[List[EntityModel]] = None
    themes: Optional[List[str]] = None
    entity_count: Optional[int] = None
    paint_options: Optional[dict] = Field(None)
    attribution: Optional[str] = None
    attribution_text: Optional[str] = None
    licence: Optional[str] = None
    licence_text: Optional[str] = None
    consideration: Optional[str] = None
    github_discussion: Optional[int] = None
    entity_minimum: Optional[int] = None
    entity_maximum: Optional[int] = None
    phase: Optional[str] = None
    realm: Optional[str] = None
    replacement_dataset: Optional[str] = None
    version: Optional[str] = None


class TypologyModel(DigitalLandDateFieldsModel):
    typology: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    plural: Optional[str] = None
    text: Optional[str] = None
    wikidata: Optional[str] = None
    wikipedia: Optional[str] = None


class OrganisationModel(DigitalLandDateFieldsModel):
    organisation: Optional[str] = None
    name: Optional[str] = None
    combined_authority: Optional[str] = None
    entity: Optional[int] = None
    local_authority_type: Optional[str] = None
    official_name: Optional[str] = None
    region: Optional[str] = None
    statistical_geography: Optional[str] = None
    website: Optional[str] = None


class OrganisationsByTypeModel(BaseModel):
    organisations: Dict[str, List[OrganisationModel]]


class DatasetCollectionModel(DigitalLandBaseModel):
    dataset_collection: Optional[str] = None
    resource: Optional[str] = None
    resource_end_date: Optional[date] = None
    resource_entry_date: Optional[date] = None
    last_updated: Optional[date] = None
    last_collection_attempt: Optional[date] = None


class DatasetPublicationCountModel(DigitalLandBaseModel):
    dataset_publication: str
    expected_publisher_count: int
    publisher_count: int


def entity_factory(entity_orm: EntityOrm):
    e = EntityModel.model_validate(entity_orm)
    if entity_orm.json is not None:
        # if values in json present then extend the pydantic model
        # TODO could add in additional validation using field informtion
        field_definitions = {
            to_snake(key): (Any, None) for key in entity_orm.json.keys()
        }
        ExtendedEntityModel = create_model(
            "ExtendedEntityModel", **field_definitions, __base__=EntityModel
        )

        # use new model with the added json fields
        e = ExtendedEntityModel(**e.model_dump(by_alias=False), **entity_orm.json)

    return e


class TaskModel(DigitalLandBaseModel):
    reference: str
    dataset: str
    organisation: Optional[str] = None
    endpoint: Optional[str] = None
    resource: Optional[str] = None
    details: Optional[dict] = None
    severity: str
    responsibility: str
    task_source: str
    entry_date: Optional[date] = None


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


class FieldModel(DigitalLandBaseModel):
    field: str
    datatype: str
    name: str
    typology: str
    uri_template: Optional[str] = None
