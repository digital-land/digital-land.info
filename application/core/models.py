from datetime import date
from typing import Optional, List, Dict, Any

from geoalchemy2.shape import to_shape
from geoalchemy2.elements import WKBElement, WKTElement
from pydantic import BaseModel, Field, validator, Extra, create_model

from application.db.models import EntityOrm
from application.core.utils import to_snake


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


# cannot currently accept raw strings for geometry and
def _make_geometry(v, values) -> str:
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
    attribution: str = None
    attribution_text: str = None
    licence: str = None
    licence_text: str = None


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

    if hasattr(entity_orm, "json") and entity_orm.json is not None:
        # if values in json present then extend the pydantic model
        # TODO could add in additional validation using field informtion
        field_definitions = {
            to_snake(key): (Any, None) for key in entity_orm.json.keys()
        }
        ExtendedEntityModel = create_model(
            "ExtendedEntityModel", **field_definitions, __base__=EntityModel
        )

        # use new model with the added json fields
        e = ExtendedEntityModel(**e.dict(by_alias=False), **entity_orm.json)

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


class FieldModel(DigitalLandBaseModel):
    field: str
    datatype: str
    name: str
    typology: str
    uri_template: Optional[str] = None
