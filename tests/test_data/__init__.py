import json
import sys
import csv
from pathlib import Path

csv.field_size_limit(sys.maxsize)


def load_data(name, delimiter="|"):
    csv.register_dialect("piped", delimiter=delimiter, quoting=csv.QUOTE_ALL)
    data = []
    p = Path(__file__).with_name(f"{name}.csv")
    with open(p) as f:
        reader = csv.DictReader(f, dialect="piped")
        for row in reader:
            r = {}
            for key, val in row.items():
                if val:
                    if key in ["json", "geojson", "paint_options"] and val:
                        r[key] = json.loads(val)
                    else:
                        r[key] = val
                else:
                    r[key] = None
            data.append(r)
    return data


datasets = load_data("datasets")
entities = load_data("entities")
invalid_geometry = load_data("invalid_geometry", delimiter=",")
