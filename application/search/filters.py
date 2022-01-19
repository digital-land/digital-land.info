import datetime

from dataclasses import dataclass
from typing import Optional, List
from fastapi import Query, Header

from application.search.enum import EntriesOption, DateOption, GeometryRelation, Suffix


@dataclass
class QueryFilters:

    # base filters
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
    geometry_entity: Optional[List[str]] = Query(
        None, description="take the geometry from each of these entities"
    )
    geometry_reference: Optional[List[str]] = Query(
        None, description="take the geometry from the entities with these references"
    )
    geometry_relation: Optional[GeometryRelation] = Query(
        None, description="DE-9IM spatial relationship, default is 'intersects'"
    )

    # pagination filters
    limit: Optional[int] = Query(
        10, description="limit for the number of results", ge=1
    )
    offset: Optional[int] = Query(None, description="paginate results from this entity")

    # response format filters
    accept: Optional[str] = Header(
        None, description="accepted content-type for results"
    )
    suffix: Optional[Suffix] = Query(None, description="file format for the results")
