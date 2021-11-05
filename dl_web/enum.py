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


class GeometryMatch(str, Enum):
    intersets = "intersects"
    contains = "contains"
    overlaps = "overlaps"
    crosses = "crosses"
    touches = "touches"


class EntriesOption(str, Enum):
    all = "all"
    current = "current"
    historical = "historical"


class DateOption(str, Enum):
    match = "match"
    before = "before"
    since = "since"
