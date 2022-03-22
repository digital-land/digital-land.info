import datetime
from enum import Enum

from typing import Optional, List
from fastapi import Query, Header
from pydantic import validator
from pydantic.dataclasses import dataclass

from application.core.models import EntityModel
from application.db.models import DatasetOrm
from application.db.session import get_context_session
from application.exceptions import DatasetValueNotFound
from application.search.enum import EntriesOption, DateOption, GeometryRelation, Suffix

ENTITY_MODEL_FIELDS = list(EntityModel.schema()["properties"].keys())
ENTITY_MODEL_FIELD_ENUM = Enum("field", zip(ENTITY_MODEL_FIELDS, ENTITY_MODEL_FIELDS))


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
        10, description="limit for the number of results", ge=1, le=500
    )
    offset: Optional[int] = Query(None, description="paginate results from this entity")

    # response format filters
    accept: Optional[str] = Header(
        None, description="accepted content-type for results"
    )
    suffix: Optional[Suffix] = Query(None, description="file format for the results")
    field: Optional[List[ENTITY_MODEL_FIELD_ENUM]] = Query(
        None, description="fields to be included in response"
    )

    @validator("dataset", pre=True)
    def datasets_exist(cls, v: Optional[list]):
        if not v:
            return v
        with get_context_session() as session:
            dataset_names = session.query(DatasetOrm.dataset).all()
        missing_datasets = set(v).difference(set(dataset_names))
        if missing_datasets:
            raise DatasetValueNotFound(
                f"Requested datasets do not exist: {','.join(missing_datasets)}. "
                f"Valid dataset names: {','.join(dataset_names)}",
                dataset_names=dataset_names,
            )
        return v
