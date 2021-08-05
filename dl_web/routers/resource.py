import csv
import logging
from collections import defaultdict
from datetime import date, datetime

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from ..data_store import datastore, organisation
from ..resources import templates

router = APIRouter(prefix="/resource")
logger = logging.getLogger(__name__)
collection = datastore.collection


@router.get("/", response_class=HTMLResponse)
def resource_index(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "collection": collection}
    )


@router.get("/{resource_hash}", response_class=HTMLResponse)
def resource(request: Request, resource_hash: str):
    payload = {}

    try:
        resource_endpoints = collection.resource_endpoints(resource_hash)
    except KeyError:
        raise HTTPException(status_code=404, detail="Resource not found")

    payload["resource"] = resource_hash

    # TODO Sanity check this logic... taking arbitrary items from a list makes me nervous
    #      Maybe we should return a list of collections?
    collection_name = collection.source.records[resource_endpoints[0]][0]["collection"]
    payload["collection"] = collection_name

    transformed = datastore.fetch(collection_name, resource_hash, "transformed")
    reader = csv.DictReader(transformed.open())
    count = 0
    ended_count = 0
    organisations = []
    organisations_seen = set()
    data = []
    for row in reader:
        count += 1
        if row["end-date"]:
            end_date = date.fromisoformat(row["end-date"])
            if end_date <= date.today():
                ended_count += 1

        org = row.get("organisation", None)
        if org and org not in organisations_seen:
            organisations_seen.add(org)
            organisations.append(
                {"name": organisation.organisation[org]["name"], "id": org}
            )

        data.append(row)

    payload["summary"] = {
        "records": {"total": count, "ended": ended_count},
        "organisations": organisations,
    }

    # Issue
    issue = datastore.fetch(collection_name, resource_hash, "issue")
    issues = defaultdict(
        lambda: {"rows": list(), "issues": list(), "total": 0, "samples": list()}
    )
    for i in csv.DictReader(issue.open()):
        issues[i["issue-type"]]["issues"].append(i)
        row_number = int(i["row-number"])
        issues[i["issue-type"]]["rows"].append(row_number)
        issues[i["issue-type"]]["total"] += 1
        if issues[i["issue-type"]]["total"] < 10:
            issues[i["issue-type"]]["samples"].append(data[row_number - 1])

    payload["issues"] = issues

    endpoints = []
    for e in resource_endpoints:
        endpoint_record = collection.endpoint.records[e][-1]
        organisations = []
        orgs_seen = set()
        for source in collection.source.records[e]:
            org = source["organisation"]
            if not org or org in orgs_seen:
                continue
            organisations.append(
                {"name": organisation.organisation[org]["name"], "id": org}
            )

        success_logs = list(
            filter(lambda x: x["status"] == "200", collection.log.records[e])
        )
        first = success_logs[0]
        last = success_logs[-1]

        endpoints.append(
            {
                "endpoint_url": endpoint_record["endpoint-url"],
                "organisations": organisations,
                "start_date": format_date(first["entry-date"]),
                "last_collected": format_date(last["entry-date"]),
            }
        )

    payload["endpoints"] = endpoints

    files = []
    # Collected
    files.append(
        {
            "name": "Collected",
            "format": "UNKNOWN",
            "size": "{:,.2f} KB".format(
                int(collection.resource.records[resource_hash][-1]["bytes"]) / 1024
            ),
            "href": resource_url(collection_name, resource_hash, "collected"),
        }
    )

    # Transformed
    files.append(
        {
            "name": "Transformed",
            "format": "CSV",
            "size": "{:,.2f} KB".format(transformed.stat().st_size / 1024),
            "href": resource_url(collection_name, resource_hash, "transformed"),
        }
    )

    payload["files"] = files

    return templates.TemplateResponse(
        "resource-no-table.html",
        {
            "request": request,
            "resource": payload,
            "data": data,
            "issues": issues,
            "collection": collection,
        },
    )


def format_date(value):
    return datetime.fromisoformat(value).date()


def resource_url(collection, resource_hash, stage):
    if stage == "transformed":
        return f"https://collection-dataset.s3.eu-west-2.amazonaws.com/{collection}-collection/transformed/{collection}/{resource_hash}.csv"
    elif stage == "collected":
        return f"https://collection-dataset.s3.eu-west-2.amazonaws.com/{collection}-collection/collection/resource/{resource_hash}"
    else:
        raise ValueError(f"invalid stage {stage}")
