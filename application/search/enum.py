from enum import Enum


class SuffixLinkableFiles(str, Enum):
    csv = "csv"


class SuffixEntity(str, Enum):
    json = "json"
    html = "html"
    geojson = "geojson"


class SuffixDataset(str, Enum):
    json = "json"
    html = "html"


class SuffixOrganisation(str, Enum):
    json = "json"
    html = "html"


class PointMatch(str, Enum):
    within = "within"


# https://en.wikipedia.org/wiki/DE-9IM
class GeometryRelation(str, Enum):
    within = "within"  # our default
    equals = "equals"
    disjoint = "disjoint"
    intersects = "intersects"
    touches = "touches"
    contains = "contains"
    covers = "covers"
    coveredby = "coveredby"
    overlaps = "overlaps"
    crosses = "crosses"
    # PostGiS and a distance paramter are needed for a Dwithin
    # https://postgis.net/workshops/postgis-intro/spatial_relationships.html
    # dwithin = "dwithin"


class PeriodOption(str, Enum):
    all = "all"
    current = "current"
    historical = "historical"


class DateOption(str, Enum):
    match = "match"
    before = "before"
    since = "since"
    empty = "empty"
