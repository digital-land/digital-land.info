import datetime

from typing import Optional, List
from fastapi import Query, Header
from pydantic import validator
from pydantic.dataclasses import dataclass
from sqlalchemy import text

from application.db.models import DatasetOrm
from application.db.session import get_context_session
from application.exceptions import (
    DatasetValueNotFound,
    InvalidGeometry,
    DigitalLandValidationError,
)
from application.search.enum import (
    EntriesOption,
    DateOption,
    GeometryRelation,
    SuffixEntity,
)
from application.search.custom_data_types import FormInt
from application.search.validators import (
    validate_dataset_name,
    validate_day_integer,
    validate_month_integer,
    validate_year_integer,
)


@dataclass
class DatasetQueryFilters:
    dataset: str = Query(None)

    @validator("dataset", pre=True)
    def datasets_exist(cls, dataset: str):
        with get_context_session() as session:
            dataset_names = [
                result[0]
                for result in session.query(DatasetOrm.dataset)
                .where(DatasetOrm.typology != "specification")
                .all()
            ]
        if dataset not in dataset_names:
            raise DatasetValueNotFound(
                f"Requested dataset does not exist: {dataset}. "
                f"Valid dataset names: {','.join(dataset_names)}",
                dataset_names=dataset_names,
            )
        return dataset


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
    organisation: Optional[List[str]] = Query(None, include_in_schema=False)

    organisation_entity: Optional[List[int]] = Query(
        None,
        description="Search for entities managed by organisation",
    )
    entity: Optional[List[int]] = Query(
        None, description="Search for entities by entity number"
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

    # date filters all use our custom FormIn data type, this allows empty strings to be submitted as parameter values
    # this does not need to be used for required parameters or path parameters
    start_date: Optional[datetime.date] = Query(None, include_in_schema=False)
<<<<<<< HEAD
    start_date_year: Optional[str] = Query(
=======
    start_date_year: Optional[FormInt] = Query(
>>>>>>> fix form validation issues add acceptance test for running blank search
        None,
        description="""
        Search for entities by start date year before or after the given year. Depends on start_date_match
        """,
    )
<<<<<<< HEAD
    start_date_month: Optional[str] = Query(
=======
    start_date_month: Optional[FormInt] = Query(
>>>>>>> fix form validation issues add acceptance test for running blank search
        None,
        description="""
        Search for entities by start date month before or after the given year. Depends on start_date_match
        """,
    )
<<<<<<< HEAD
    start_date_day: Optional[str] = Query(
=======
    start_date_day: Optional[FormInt] = Query(
>>>>>>> fix form validation issues add acceptance test for running blank search
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
<<<<<<< HEAD
    end_date_year: Optional[str] = Query(
        None,
        description="""Search by end date year before or after the given year. Depends on end_date_match""",
    )
    end_date_month: Optional[str] = Query(
=======
    end_date_year: Optional[FormInt] = Query(
        None,
        description="""Search by end date year before or after the given year. Depends on end_date_match""",
    )
    end_date_month: Optional[FormInt] = Query(
>>>>>>> fix form validation issues add acceptance test for running blank search
        None,
        description="""
        Search for entities by end date month before or after the given month.Depends on end_date_match
        """,
    )
<<<<<<< HEAD
    end_date_day: Optional[str] = Query(
=======
    end_date_day: Optional[FormInt] = Query(
>>>>>>> fix form validation issues add acceptance test for running blank search
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
<<<<<<< HEAD
    entry_date_year: Optional[str] = Query(
=======
    entry_date_year: Optional[FormInt] = Query(
>>>>>>> fix form validation issues add acceptance test for running blank search
        None,
        description="""
        Search for entities by entry date year before or after the given year. Depends on entry_date_match
        """,
    )
<<<<<<< HEAD
    entry_date_month: Optional[str] = Query(
=======
    entry_date_month: Optional[FormInt] = Query(
>>>>>>> fix form validation issues add acceptance test for running blank search
        None,
        description="""
        Search for entities for entities by entry date month before or after the given month.Depends on entry_date_match
        """,
    )
<<<<<<< HEAD
    entry_date_day: Optional[str] = Query(
=======

    entry_date_day: Optional[FormInt] = Query(
>>>>>>> fix form validation issues add acceptance test for running blank search
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
        Search for entities with geometries intersecting with one or more geometries provided in WKT format""",
    )
    geometry_entity: Optional[List[int]] = Query(
        None,
        description="""Search for entities with geometries intersecting with one or more geometries
        taken from each of the provided entities""",
    )
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
    field: Optional[List[str]] = Query(
        None, description="fields to be included in response"
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

    @validator("dataset", pre=True)
    def datasets_exist(cls, v: Optional[list]):
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

    @validator("geometry", pre=True)
    def geometry_valid(cls, v: Optional[list]):
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

    @validator("entry_date_day", "start_date_day", "end_date_day", pre=True)
    def validate_date_day(cls, v, field):
        if isinstance(v, str):
            if v.strip() == "":
                return v
            try:
                day = int(v)
                if 1 <= day <= 31:
                    return day
                else:
                    raise DigitalLandValidationError(
                        f"field {field} must be a number between 1 and 31"
                    )
            except Exception:
                raise DigitalLandValidationError(
                    f"field {field} must be a number between 1 and 31"
                )
        return v

    @validator("entry_date_month", "start_date_month", "end_date_month", pre=True)
    def validate_date_month(cls, v, field):
        if isinstance(v, str):
            if v.strip() == "":
                return v
            try:
                month = int(v)
                if 1 <= month <= 12:
                    return month
                else:
                    raise DigitalLandValidationError(
                        f"field {field} must be a number between 1 and 12"
                    )
            except Exception:
                raise DigitalLandValidationError(
                    f"field {field} must be a number between 1 and 12"
                )
        return v

    @validator("entry_date_year", "start_date_year", "end_date_year", pre=True)
    def validate_date_year(cls, v, field):
        if isinstance(v, str):
            if v.strip() == "":
                return v
            try:
                year = int(v)
                return year
            except Exception:
                raise DigitalLandValidationError(f"field {field} must be numeric")
        return v

    @validator("curie", "geometry_curie", pre=True)
    def validate_curie(cls, values: Optional[list]):
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
def get_dataset_names():
    with get_context_session() as session:
        dataset_names = [
            result[0]
            for result in session.query(DatasetOrm.dataset)
            .where(DatasetOrm.typology != "specification")
            .all()
        ]
    return dataset_names


@dataclass
class FactDatasetQueryFilters:
    dataset: str

    @validator("dataset", pre=True)
    def datasets_exist(cls, dataset: str):
        dataset_names = get_dataset_names()
        if dataset not in dataset_names:
            raise DatasetValueNotFound(
                f"Requested dataset does not exist: {dataset}. "
                f"Valid dataset names: {','.join(dataset_names)}",
                dataset_names=dataset_names,
            )
        return dataset


@dataclass
class FactQueryFilters(FactDatasetQueryFilters):
    entity: int
    field: Optional[List[str]] = Query(None)
