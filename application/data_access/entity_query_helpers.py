import datetime
import operator

from application.db.models import EntityOrm
from application.search.enum import DateOption, GeometryRelation


def get_date_field_to_filter(date_field):
    if date_field == "start_date":
        return EntityOrm.start_date
    if date_field == "end_date":
        return EntityOrm.end_date
    if date_field == "entry_date":
        return EntityOrm.entry_date
    return None


def get_date_to_filter(date_field, params):
    try:
        year = int(params.get(date_field + "_year", 0))
        if year:
            month = int(params.setdefault(date_field + "_month", 1))
            day = int(params.setdefault(date_field + "_day", 1))
            return datetime.date(year, month, day)
        else:
            return None
    except ValueError:
        return None


def get_operator(params):
    match = params.get("entry_date_match", None)
    if match is None:
        return operator.eq
    if match == DateOption.before:
        return operator.lt
    if match == DateOption.since:
        return operator.gt
    return None


def get_point(params):
    if "longitude" in params and "latitude" in params:
        return f"POINT({params['longitude']} {params['latitude']})"
    return None


def get_spatial_function_for_relation(relation):
    from sqlalchemy import func

    if relation == GeometryRelation.intersects:
        return func.ST_Intersects
    if relation == GeometryRelation.equals:
        return func.ST_Equals
    if relation == GeometryRelation.disjoint:
        return func.ST_Disjoint
    if relation == GeometryRelation.touches:
        return func.ST_Touches
    if relation == GeometryRelation.contains:
        return func.ST_Contains
    if relation == GeometryRelation.covers:
        return func.ST_Covers
    if relation == GeometryRelation.coveredby:
        return func.ST_CoveredBy
    if relation == GeometryRelation.overlaps:
        return func.ST_Overlaps
    if relation == GeometryRelation.crosses:
        return func.ST_Crosses

    return func.ST_Within


def normalised_params(params):
    lists = [
        "typology",
        "dataset",
        "entity",
        "prefix",
        "reference",
        "organisation_entity",
    ]

    params = {k: v for k, v in params.items() if v}

    for lst in lists:
        if lst in params:
            params[lst] = [v for v in params[lst] if v]
            params[lst] = sorted(set(params[lst]))

    return params
