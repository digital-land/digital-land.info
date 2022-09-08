import datetime

from typing import Optional, List
from fastapi import Query, Header
from pydantic import validator
from pydantic.dataclasses import dataclass
from sqlalchemy import text
from application.data_access.digital_land_queries import get_typology_names

from application.db.models import DatasetOrm
from application.db.session import get_context_session
from application.exceptions import (
    DatasetValueNotFound,
    TypologyValueNotFound,
    InvalidGeometry,
    DigitalLandValidationError,
)
from application.search.enum import (
    EntriesOption,
    DateOption,
    GeometryRelation,
    SuffixEntity,
)

from application.search.validators import validate_dataset_name


@dataclass
class DatasetQueryFilters:
    dataset: str = Query(None)

    # validators
    _validate_dataset_name = validator("dataset", allow_reuse=True)(
        validate_dataset_name
    )


@dataclass
class QueryFilters:

    # base filters
    theme: Optional[List[str]] = Query(None, include_in_schema=False)
    typology: Optional[List[str]] = Query(
        None,
        description="Search for entities by typology",
    )
    dataset: Optional[List[str]] = Query(
        None,
        description="Search for entities by dataset",
    )

    # TODO implement this like curie and subselect
    #  I do not think either of these are included in the query yet
    organisation: Optional[List[str]] = Query(None, include_in_schema=False)

    organisation_entity: Optional[List[int]] = Query(
        None, description="Search for entities managed by organisation", ge=1
    )

    entity: Optional[List[int]] = Query(
        None, description="Search for entities by entity number", ge=1
    )

    curie: Optional[List[str]] = Query(None, description="Search for entities by CURIE")

    prefix: Optional[List[str]] = Query(
        None, description="Search for entities by prefix"
    )
    reference: Optional[List[str]] = Query(
        None, description="Search for entities by reference"
    )

    # TODO remove not implemented
    # related_entity: Optional[List[str]] = Query(
    #     None, description="filter by related entity"
    # )

    entries: Optional[EntriesOption] = Query(
        None, description="Results to include current, or all entries"
    )

    # date filters
    start_date: Optional[datetime.date] = Query(None, include_in_schema=False)
    start_date_year: Optional[int] = Query(
        None,
        description="""
        Search for entities by start date year before or after the given year. Depends on start_date_match
        """,
        ge=1,
    )
    start_date_month: Optional[int] = Query(
        None,
        description="""
        Search for entities by start date month before or after the given year. Depends on start_date_match
        """,
        ge=1,
        le=12,
    )
    start_date_day: Optional[int] = Query(
        None,
        description="""
        Search for entities by start date day before or after the given day. Depends on start_date_match
        """,
        ge=1,
        le=31,
    )
    start_date_match: Optional[DateOption] = Query(
        None,
        description="Specify how to filter against the start_date_* values provided, either before, after or match",
    )

    end_date: Optional[datetime.date] = Query(None, include_in_schema=False)
    end_date_year: Optional[int] = Query(
        None,
        description="""Search by end date year before or after the given year. Depends on end_date_match""",
        ge=1,
    )
    end_date_month: Optional[int] = Query(
        None,
        description="""
        Search for entities by end date month before or after the given month.Depends on end_date_match
        """,
        ge=1,
        le=12,
    )
    end_date_day: Optional[int] = Query(
        None,
        description="""
        Search for entities by end date day before or after the given day. Depends on end_date_match
        """,
        ge=1,
        le=31,
    )
    end_date_match: Optional[DateOption] = Query(
        None,
        description="""Specify how to filter against the end_date_* values provided, either before, after or match""",
    )

    entry_date: Optional[datetime.date] = Query(None, include_in_schema=False)
    entry_date_year: Optional[int] = Query(
        None,
        description="""
        Search for entities by entry date year before or after the given year. Depends on entry_date_match
        """,
        ge=1,
    )
    entry_date_month: Optional[int] = Query(
        None,
        description="""
        Search for entities for entities by entry date month before or after the given month.Depends on entry_date_match
        """,
        ge=1,
        le=12,
    )
    entry_date_day: Optional[int] = Query(
        None,
        description="""
        Search for entities by entry date day before or after the given day. Depends on entry_date_match
        """,
        ge=1,
        le=31,
    )
    entry_date_match: Optional[DateOption] = Query(
        None,
        description="""
        Specify for entities how to filter against the entry_date_* values provided, either before, after or match
        """,
    )

    # spatial filters
    longitude: Optional[float] = Query(
        None,
        description="""
        Search for entity with geometries intersected by a point constructed with this longitude.
        Requires latitude to be provided.
        """,
    )
    latitude: Optional[float] = Query(
        None,
        description="""
        Search for entities with geometries intersected by a point constructed with this latitude.
        Requires longitude to be provided.
        """,
    )
    geometry: Optional[List[str]] = Query(
        None,
        description="""
        Search for entities with geometries intersecting with one or more geometries provided in WKT format""",
    )
    geometry_entity: Optional[List[int]] = Query(
        None,
        description="""Search for entities with geometries intersecting with one or more geometries
        taken from each of the provided entities""",
        ge=1,
    )
    # should we get riid of this, people should aimi to use curies not random reference
    geometry_reference: Optional[List[str]] = Query(
        None,
        description="""
        Search entities with geometries intersecting with the geometries of
        entities with the provided references
        """,
    )
    geometry_curie: Optional[List[str]] = Query(
        None,
        description="""
        Search for entities with geometries intersecting with geometries
        entities matching provided curies
        """,
    )
    geometry_relation: Optional[GeometryRelation] = Query(
        None, description="DE-9IM spatial relationship, default is 'within'"
    )

    # pagination filters
    limit: Optional[int] = Query(
        10, description="limit for the number of results", ge=1, le=500
    )
    offset: Optional[int] = Query(None, description="paginate results from this entity")

    # response format filters
    accept: Optional[str] = Header(
        None, description="accepted content-type for results", include_in_schema=False
    )
    suffix: Optional[SuffixEntity] = Query(
        None, description="file format for the results", include_in_schema=False
    )
    # once field is included in codebase we can update this
    field: Optional[List[str]] = Query(
        None, description="fields to be included in response"
    )

    @validator("dataset", pre=True)
    def validate_datasets(cls, v: Optional[list]):
        if not v:
            return v
        with get_context_session() as session:
            dataset_names = [
                result[0] for result in session.query(DatasetOrm.dataset).all()
            ]
        missing_datasets = set(v).difference(set(dataset_names))
        if missing_datasets:
            raise DatasetValueNotFound(
                f"Requested datasets do not exist: {','.join(missing_datasets)}. "
                f"Valid dataset names: {','.join(dataset_names)}",
                dataset_names=dataset_names,
            )
        return v

    @validator("typology", pre=True)
    def validate_typologies(cls, typologies):
        if not typologies:
            return typologies
        typology_names = get_typology_names()
        missing_typologies = set(typologies).difference(set(typology_names))
        if missing_typologies:
            raise TypologyValueNotFound(
                f"Requested datasets do not exist: {','.join(missing_typologies)}. "
                f"Valid dataset names: {','.join(typology_names)}",
                dataset_names=typology_names,
            )
        return typologies

    @validator("geometry", pre=True)
    def validate_geometry(cls, v: Optional[list]):
        if not v:
            return v
        with get_context_session() as session:
            for geometry in v:
                try:
                    stmt = text("SELECT ST_IsValid(:geometry);")
                    stmt = stmt.bindparams(geometry=geometry)
                    session.execute(stmt)
                except Exception:
                    raise InvalidGeometry(f"Invalid geometry {geometry}")
        return v

    @validator("curie", "geometry_curie", pre=True)
    def validate_curies(cls, values: Optional[list]):
        if not values:
            return values
        for v in values:
            parts = v.split(":")
            if len(parts) < 2 or not all(parts):
                raise DigitalLandValidationError(
                    "curie must be in form 'prefix:reference'"
                )
        return values


# need separate classes for fact pages as dataset is not optional, this should be easy by expanding classes


@dataclass
class FactDatasetQueryFilters:
    dataset: str

    # validators
    _validate_dataset_name = validator("dataset", allow_reuse=True)(
        validate_dataset_name
    )


@dataclass
class FactQueryFilters(FactDatasetQueryFilters):
    entity: int = Query(default=..., ge=1)
    # need to add validatiion onto the below however this should be done once the field table has been included into
    # the postgis database
    field: Optional[List[str]] = Query(None)


@dataclass
class FactPathParams:
    fact: str = Query(default=..., regex="^[a-f0-9]{64}$")
