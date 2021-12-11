import datetime

from dataclasses import dataclass
from typing import Optional, List
from fastapi import Query, Header

from dl_web.search.enum import EntriesOption, DateOption, GeometryRelation, Suffix


@dataclass
class BaseFilters:
    theme: Optional[List[str]] = Query(None)
    typology: Optional[List[str]] = Query(None)
    dataset: Optional[List[str]] = Query(None)
    organisation: Optional[List[str]] = Query(None)
    organisation_entity: Optional[List[str]] = Query(None)
    entity: Optional[List[str]] = Query(None)
    curie: Optional[List[str]] = Query(None)
    prefix: Optional[List[str]] = Query(None)
    reference: Optional[List[str]] = Query(None)
    related_entity: Optional[List[str]] = Query(
        None, description="filter by related entity"
    )
    entries: Optional[EntriesOption] = Query(
        None, description="Results to include current, or all entries"
    )


@dataclass
class DateFilters:
    # TODO: remove the spurious "entry_" prefixes to these filters
    entry_start_date: Optional[datetime.date] = None
    entry_start_date_year: Optional[str] = None
    entry_start_date_month: Optional[str] = None
    entry_start_date_day: Optional[str] = None
    entry_start_date_match: Optional[DateOption] = None
    entry_end_date: Optional[datetime.date] = None
    entry_end_date_year: Optional[str] = None
    entry_end_date_month: Optional[str] = None
    entry_end_date_day: Optional[str] = None
    entry_end_date_match: Optional[DateOption] = None
    entry_entry_date: Optional[datetime.date] = None
    entry_entry_date_year: Optional[str] = None
    entry_entry_date_month: Optional[str] = None
    entry_entry_date_day: Optional[str] = None
    entry_entry_date_match: Optional[DateOption] = None


@dataclass
class SpatialFilters:
    longitude: Optional[float] = Query(
        None, description="construct a point with this longitude"
    )
    latitude: Optional[float] = Query(
        None, description="construct a point with this latitude"
    )
    geometry: Optional[List[str]] = Query(
        None, description="one or more geometries in WKT format"
    )
    geometry_entity: Optional[List[str]] = Query(
        None, description="take the geometry from each of these entities"
    )
    geometry_reference: Optional[List[str]] = Query(
        None, description="take the geometry from the entities with these references"
    )
    geometry_relation: Optional[GeometryRelation] = Query(
        None, description="DE-9IM spatial relationship, default is 'intersects'"
    )


@dataclass
class PaginationFilters:
    limit: Optional[int] = Query(
        10, description="limit for the number of results", ge=1
    )
    next_entity: Optional[int] = Query(
        None, description="paginate results from this entity"
    )


@dataclass
class FormatFilters:
    # response format
    accept: Optional[str] = Header(
        None, description="accepted content-type for results"
    )
    suffix: Optional[Suffix] = Query(None, description="file format for the results")
