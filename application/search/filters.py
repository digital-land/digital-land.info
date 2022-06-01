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
    theme: Optional[List[str]] = Query(None)
    typology: Optional[List[str]] = Query(None)
    dataset: Optional[List[str]] = Query(None)

    # TODO implement this like curie and subselect
    organisation: Optional[List[str]] = Query(None)

    organisation_entity: Optional[List[int]] = Query(None)
    entity: Optional[List[int]] = Query(None)
    curie: Optional[List[str]] = Query(None)
    prefix: Optional[List[str]] = Query(None)
    reference: Optional[List[str]] = Query(None)

    # TODO remove not implemented
    # related_entity: Optional[List[str]] = Query(
    #     None, description="filter by related entity"
    # )

    entries: Optional[EntriesOption] = Query(
        None, description="Results to include current, or all entries"
    )

    # date filters
    start_date: Optional[datetime.date] = None
    start_date_year: Optional[str] = None
    start_date_month: Optional[str] = None
    start_date_day: Optional[str] = None
    start_date_match: Optional[DateOption] = None

    end_date: Optional[datetime.date] = None
    end_date_year: Optional[str] = None
    end_date_month: Optional[str] = None
    end_date_day: Optional[str] = None
    end_date_match: Optional[DateOption] = None

    entry_date: Optional[datetime.date] = None
    entry_date_year: Optional[str] = None
    entry_date_month: Optional[str] = None
    entry_date_day: Optional[str] = None
    entry_date_match: Optional[DateOption] = None

    # spatial filters
    longitude: Optional[float] = Query(
        None, description="construct a point with this longitude"
    )
    latitude: Optional[float] = Query(
        None, description="construct a point with this latitude"
    )
    geometry: Optional[List[str]] = Query(
        None, description="one or more geometries in WKT format"
    )
    geometry_entity: Optional[List[int]] = Query(
        None, description="take the geometry from each of these entities"
    )
    geometry_reference: Optional[List[str]] = Query(
        None, description="take the geometry from the entities with these references"
    )
    geometry_relation: Optional[GeometryRelation] = Query(
        None, description="DE-9IM spatial relationship, default is 'within'"
    )
    geometry_curie: Optional[List[str]] = Query(
        None, description="take the geometry from the entities with these curies"
    )

    # pagination filters
    limit: Optional[int] = Query(
        10, description="limit for the number of results", ge=1, le=500
    )
    offset: Optional[int] = Query(None, description="paginate results from this entity")

    # response format filters
    accept: Optional[str] = Header(
        None, description="accepted content-type for results"
    )
    suffix: Optional[SuffixEntity] = Query(
        None, description="file format for the results"
    )
    field: Optional[List[str]] = Query(
        None, description="fields to be included in response"
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
