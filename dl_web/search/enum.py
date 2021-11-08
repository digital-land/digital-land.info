from enum import Enum


class Suffix(str, Enum):
    json = "json"
    html = "html"
    xlsx = "xlsx"
    zip = "zip"
    csv = "csv"
    ttl = "ttl"


class PointMatch(str, Enum):
    within = "within"


# https://en.wikipedia.org/wiki/DE-9IM
class GeometryRelation(str, Enum):
    within = "within"  # our default
    equals = "equals"
    disjoint = "disjoint"
    intersets = "intersects"
    touches = "touches"
    contains = "contains"
    covers = "covers"
    coveredby = "coveredby"
    overlaps = "overlaps"
    crosses = "crosses"
    # PostGiS and a distance paramter are needed for a Dwithin
    # https://postgis.net/workshops/postgis-intro/spatial_relationships.html
    # dwithin = "dwithin"


class EntriesOption(str, Enum):
    all = "all"
    current = "current"
    historical = "historical"


class DateOption(str, Enum):
    match = "match"
    before = "before"
    since = "since"
    empty = "empty"
