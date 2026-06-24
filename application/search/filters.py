import datetime

from typing import Annotated, Optional, List
from fastapi import Query, Header
from pydantic import field_validator
from pydantic.dataclasses import dataclass

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
from shapely import wkt
from shapely.geometry.base import BaseGeometry


@dataclass
class DatasetQueryFilters:
    dataset: Annotated[
        Optional[List[str]], Query(description="Search for datasets by dataset")
    ] = None
    field: Annotated[
        Optional[List[str]],
        Query(description="Fields to include in dataset JSON response"),
    ] = None
    exclude_field: Annotated[
        Optional[List[str]],
        Query(description="Fields to exclude from the dataset JSON response"),
    ] = None
    include_typologies: bool = Query(
        True,
        description="Include typologies in dataset JSON response; set to false to remove",
    )


@dataclass
class QueryFilters:
    # base filters
    theme: Annotated[Optional[List[str]], Query(include_in_schema=False)] = None
    typology: Annotated[
        Optional[List[str]],
        Query(description="Search for entities by typology"),
    ] = None
    dataset: Annotated[
        Optional[List[str]],
        Query(description="Search for entities by dataset"),
    ] = None

    organisation: Annotated[Optional[List[str]], Query(include_in_schema=False)] = None

    organisation_entity: Annotated[
        Optional[List[Annotated[int, Query(ge=1)]]],
        Query(description="Search for entities managed by organisation"),
    ] = None
    entity: Annotated[
        Optional[List[Annotated[int, Query(ge=1)]]],
        Query(description="Search for entities by entity number"),
    ] = None
    curie: Annotated[
        Optional[List[str]], Query(description="Search for entities by CURIE")
    ] = None
    prefix: Annotated[
        Optional[List[str]],
        Query(description="Search for entities by prefix"),
    ] = None
    reference: Annotated[
        Optional[List[str]],
        Query(description="Search for entities by reference"),
    ] = None

    # TODO remove not implemented
    # related_entity: Optional[List[str]] = Query(
    #     None, description="filter by related entity"
    # )

    period: Annotated[
        Optional[List[PeriodOption]],
        Query(description="Results to include current, or all entries"),
    ] = None

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
    geometry: Annotated[
        Optional[List[str]],
        Query(
            description="""
        Search for entities with geometries interacting with one or more geometries provided in WKT format.
        The type of geometric relation can be set using the geometry relation parameter."""
        ),
    ] = None
    geometry_entity: Annotated[
        Optional[List[Annotated[int, Query(ge=1)]]],
        Query(
            description="""Search for entities with geometries interacting with one or more geometries
        taken from each of the provided entities. The type of geometric relation can be set using the
        geometry relation parameter."""
        ),
    ] = None
    geometry_reference: Annotated[
        Optional[List[str]],
        Query(description="""
        Search entities with geometries interacting with the geometries of
        entities with the provided references. The type of geometric relation
        can be set using the geometry relation parameter.
        """),
    ] = None
    geometry_curie: Annotated[
        Optional[List[str]],
        Query(description="""
        Search for entities with geometries interacting with geometries
        entities matching provided curies. The type of geometric relation
        can be set using the geometry relation parameter.
        """),
    ] = None
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
    field: Annotated[
        Optional[List[str]], Query(description="fields to be included in response")
    ] = None
    exclude_field: Annotated[
        Optional[List[str]],
        Query(
            description="field parameter will take over any fields specified in the exclude_field parameter"
        ),
    ] = None

    quality: Annotated[
        Optional[List[str]],
        Query(description="Search for entities by quality"),
    ] = None

    # validators
    @field_validator("entry_date_year", "start_date_year", "end_date_year")
    @classmethod
    def _validate_years(cls, v):
        return validate_year_integer(v)

    @field_validator("entry_date_month", "start_date_month", "end_date_month")
    @classmethod
    def _validate_months(cls, v):
        return validate_month_integer(v)

    @field_validator("entry_date_day", "start_date_day", "end_date_day")
    @classmethod
    def _validate_days(cls, v):
        return validate_day_integer(v)

    @field_validator("curie", "geometry_curie", "organisation")
    @classmethod
    def _validate_curies(cls, v):
        return validate_curies(v)

    @field_validator("geometry", mode="before")
    @classmethod
    def validate_geometry(cls, geometry_values_list: Optional[list]):
        if not geometry_values_list:
            return geometry_values_list
        for geometry in geometry_values_list:
            try:
                geom: BaseGeometry = wkt.loads(geometry)
                if not geom.is_valid:
                    raise InvalidGeometry(f"Invalid geometry {geometry}")
            except InvalidGeometry:
                raise
            except Exception as err:
                geometry_str = str(geometry).strip()
                if '{"type"' in geometry_str:
                    raise InvalidGeometry(
                        "Expected WKT format, received GeoJSON instead"
                    ) from err
                raise InvalidGeometry(f"Invalid geometry {geometry}") from err
        return geometry_values_list


@dataclass
class TaskQueryFilters:
    dataset: Optional[List[str]] = Query(None, description="Filter tasks by dataset")
    organisation: Optional[List[str]] = Query(
        None, description="Filter tasks by organisation"
    )
    severity: Optional[List[str]] = Query(None, description="Filter tasks by severity")
    responsibility: Optional[List[str]] = Query(
        None, description="Filter tasks by responsibility"
    )
    task_source: Optional[List[str]] = Query(None, description="Filter tasks by source")
    limit: int = Query(10, ge=1, le=500, description="Limit number of results")
    offset: int = Query(0, ge=0, description="Paginate results from this offset")


@dataclass
class FactDatasetQueryFilters:
    dataset: str


@dataclass
class FactQueryFilters(FactDatasetQueryFilters):
    entity: int = Query(default=..., ge=1)
    # need to add validatiion onto the below however this should be done once the field table has been included into
    # the postgis database
    field: Annotated[Optional[List[str]], Query()] = None


@dataclass
class FactPathParams:
    fact: str = Query(default=..., regex="^[a-f0-9]{64}$")
