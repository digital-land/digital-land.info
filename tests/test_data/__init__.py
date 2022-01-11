import csv
import json

from pathlib import Path

csv.register_dialect("piped", delimiter="|", quoting=csv.QUOTE_ALL)


def load_data(name):
    data = []
    p = Path(__file__).with_name(f"{name}.csv")
    with open(p) as f:
        reader = csv.DictReader(f, dialect="piped")
        for row in reader:
            r = {}
            for key, val in row.items():
                if val:
                    if key in ["json", "geojson"] and val:
                        r[key] = json.loads(val)
                    else:
                        r[key] = val
                else:
                    r[key] = None
            data.append(r)
    return data


datasets = load_data("datasets")
entities = load_data("entities")
