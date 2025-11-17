import datetime

from typing import Optional, List
from fastapi import Query, Header
from pydantic import validator
from pydantic.dataclasses import dataclass
from sqlalchemy import text

from application.db.session import get_context_session
from application.exceptions import (
    InvalidGeometry,
)
from application.search.enum import (
    PeriodOption,
    DateOption,
    GeometryRelation,
    SuffixEntity,
)
from application.search.custom_data_types import FormInt
from application.search.validators import (
    validate_day_integer,
    validate_month_integer,
    validate_year_integer,
    validate_curies,
)


@dataclass
class DatasetQueryFilters:
    dataset: Optional[List[str]] = Query(
        None, description="Search for datasets by dataset"
    )
    field: Optional[List[str]] = Query(
        None, description="Fields to include in dataset JSON response"
    )
    exclude_field: Optional[List[str]] = Query(
        None,
        description="Fields to exclude from the dataset JSON response",
    )
    include_typologies: bool = Query(
        True,
        description="Include typologies in dataset JSON response; set to false to remove",
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

    period: Optional[List[PeriodOption]] = Query(
        None, description="Results to include current, or all entries"
    )

    # date filters all use our custom FormIn data type, this allows empty strings to be submitted as parameter values
    # this does not need to be used for required parameters or path parameters
    start_date: Optional[datetime.date] = Query(None, include_in_schema=False)
    start_date_year: Optional[FormInt] = Query(
        None,
        description="""
        Search for entities by start date year before or after the given year. Depends on start_date_match
        """,
    )
    start_date_month: Optional[FormInt] = Query(
        None,
        description="""
        Search for entities by start date month before or after the given year. Depends on start_date_match
        """,
    )
    start_date_day: Optional[FormInt] = Query(
        None,
        description="""
        Search for entities by start date day before or after the given day. Depends on start_date_match
        """,
    )
    start_date_match: Optional[DateOption] = Query(
        None,
        description="Specify how to filter against the start_date_* values provided, either before, after or match",
    )

    end_date: Optional[datetime.date] = Query(None, include_in_schema=False)
    end_date_year: Optional[FormInt] = Query(
        None,
        description="""Search by end date year before or after the given year. Depends on end_date_match""",
    )
    end_date_month: Optional[FormInt] = Query(
        None,
        description="""
        Search for entities by end date month before or after the given month.Depends on end_date_match
        """,
    )
    end_date_day: Optional[FormInt] = Query(
        None,
        description="""
        Search for entities by end date day before or after the given day. Depends on end_date_match
        """,
    )
    end_date_match: Optional[DateOption] = Query(
        None,
        description="""Specify how to filter against the end_date_* values provided, either before, after or match""",
    )

    entry_date: Optional[datetime.date] = Query(None, include_in_schema=False)
    entry_date_year: Optional[FormInt] = Query(
        None,
        description="""
        Search for entities by entry date year before or after the given year. Depends on entry_date_match
        """,
    )
    entry_date_month: Optional[FormInt] = Query(
        None,
        description="""
        Search for entities for entities by entry date month before or after the given month.Depends on entry_date_match
        """,
    )

    entry_date_day: Optional[FormInt] = Query(
        None,
        description="""
        Search for entities by entry date day before or after the given day. Depends on entry_date_match
        """,
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
        Search for entities with geometries interacting with one or more geometries provided in WKT format.
        The type of geometric relation can be set using the geometry relation parameter.""",
    )
    geometry_entity: Optional[List[int]] = Query(
        None,
        description="""Search for entities with geometries interacting with one or more geometries
        taken from each of the provided entities. The type of geometric relation can be set using the
        geometry relation parameter.""",
        ge=1,
    )
    geometry_reference: Optional[List[str]] = Query(
        None,
        description="""
        Search entities with geometries interacting with the geometries of
        entities with the provided references. The type of geometric relation
        can be set using the geometry relation parameter.
        """,
    )
    geometry_curie: Optional[List[str]] = Query(
        None,
        description="""
        Search for entities with geometries interacting with geometries
        entities matching provided curies. The type of geometric relation
        can be set using the geometry relation parameter.
        """,
    )
    geometry_relation: Optional[GeometryRelation] = Query(
        None, description="DE-9IM spatial relationship, default is 'within'"
    )
    q: Optional[str] = Query(
        None,
        description="""
        Search by a postcode, or a Unique Property Reference Number (UPRN).
        """,
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
    # once field is updated we can validate this
    field: Optional[List[str]] = Query(
        None, description="fields to be included in response"
    )
    exclude_field: Optional[List[str]] = Query(
        None,
        description="field parameter will take over any fields specified in the exclude_field parameter",
    )

    quality: Optional[List[str]] = Query(
        None,
        description="Search for entities by quality",
    )

    # validators
    _validate_entry_date_year = validator("entry_date_year", allow_reuse=True)(
        validate_year_integer
    )
    _validate_entry_date_month = validator("entry_date_month", allow_reuse=True)(
        validate_month_integer
    )
    _validate_entry_date_day = validator("entry_date_day", allow_reuse=True)(
        validate_day_integer
    )

    _validate_start_date_year = validator("start_date_year", allow_reuse=True)(
        validate_year_integer
    )
    _validate_start_date_month = validator("start_date_month", allow_reuse=True)(
        validate_month_integer
    )
    _validate_start_date_day = validator("start_date_day", allow_reuse=True)(
        validate_day_integer
    )

    _validate_end_date_year = validator("end_date_year", allow_reuse=True)(
        validate_year_integer
    )
    _validate_end_date_month = validator("end_date_month", allow_reuse=True)(
        validate_month_integer
    )
    _validate_end_date_day = validator("end_date_day", allow_reuse=True)(
        validate_day_integer
    )

    _validate_curie = validator("curie", allow_reuse=True)(validate_curies)

    _validate_geometry_curie = validator("geometry_curie", allow_reuse=True)(
        validate_curies
    )

    _validate_organisation_curie = validator("organisation", allow_reuse=True)(
        validate_curies
    )

    # TODO Replace with a solution that doesn't need a database?
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


@dataclass
class FactDatasetQueryFilters:
    dataset: str


@dataclass
class FactQueryFilters(FactDatasetQueryFilters):
    entity: int = Query(default=..., ge=1)
    # need to add validatiion onto the below however this should be done once the field table has been included into
    # the postgis database
    field: Optional[List[str]] = Query(None)


@dataclass
class FactPathParams:
    fact: str = Query(default=..., regex="^[a-f0-9]{64}$")
