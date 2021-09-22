import csv
import logging
from collections import defaultdict
from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse

from ..data_store import DataStore, get_datastore, organisation
from ..resources import templates

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_class=HTMLResponse)
def resource_index(request: Request, datastore: DataStore = Depends(get_datastore)):
    return templates.TemplateResponse(
        "index.html", {"request": request, "collection": datastore.get_collection()}
    )


# TODO: This whole thing should be changed to get its data from the new
#       digital-land database, rather than pulling the files from S3.
#
@router.get("/{resource_hash}", response_class=HTMLResponse)
async def resource(
    request: Request,
    resource_hash: str,
    datastore: DataStore = Depends(get_datastore),
):
    payload = {}
    collection = datastore.get_collection()

    try:
        resource_endpoints = collection.resource_endpoints(resource_hash)
    except KeyError:
        raise HTTPException(status_code=404, detail="Resource not found")

    payload["resource"] = resource_hash

    # TODO Sanity check this logic... taking arbitrary items from a list makes me nervous
    #      Maybe we should return a list of collections?
    collection_name = collection.source.records[resource_endpoints[0]][0]["collection"]
    payload["collection"] = collection_name

    transformed = await datastore.fetch(collection_name, resource_hash, "transformed")
    harmonised = None
    data_table_source = transformed
    end_date_field = "end-date"
    org_field = "organisation"

    # BFL is an anomaly and needs to show the harmonised file in data table
    if collection_name in ("brownfield-land"):
        harmonised = await datastore.fetch(collection_name, resource_hash, "harmonised")
        data_table_source = harmonised
        end_date_field = "EndDate"
        org_field = "OrganisationLabel"

    reader = csv.DictReader(data_table_source.open())
    count = 0
    ended_count = 0
    organisations = []
    organisations_seen = set()
    data = []
    data_fields = reader.fieldnames
    for row in reader:
        count += 1
        if row[end_date_field]:
            end_date = date.fromisoformat(row[end_date_field])
            if end_date <= date.today():
                ended_count += 1

        org = row.get(org_field, None)
        if org and org not in organisations_seen:
            organisations_seen.add(org)
            organisations.append(
                {
                    "name": organisation.organisation[org]["name"]
                    if org_field == "organisation"
                    else org,
                    "id": org,
                }
            )

        data.append(row)

    payload["summary"] = {
        "records": {"total": count, "ended": ended_count},
        "organisations": organisations,
    }

    # Issue
    issue = await datastore.fetch(collection_name, resource_hash, "issue")
    issues = defaultdict(lambda: defaultdict(list))
    for i in csv.DictReader(issue.open()):
        issues[i["row-number"]][i["field"]].append(i)

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

    # Harmonised
    if harmonised:
        files.append(
            {
                "name": "Harmonised",
                "format": "CSV",
                "size": "{:,.2f} KB".format(harmonised.stat().st_size / 1024),
                "href": resource_url(collection_name, resource_hash, "harmonised"),
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
        "resource.html",
        {
            "request": request,
            "resource": payload,
            "data": data,
            "data_fields": data_fields,
            "issues": dict(issues),
            "collection": collection,
        },
    )


def format_date(value):
    return datetime.fromisoformat(value).date()


def resource_url(collection, resource_hash, stage):
    if stage in ("transformed", "harmonised"):
        return f"https://collection-dataset.s3.eu-west-2.amazonaws.com/{collection}-collection/{stage}/{collection}/{resource_hash}.csv"
    elif stage == "collected":
        return f"https://collection-dataset.s3.eu-west-2.amazonaws.com/{collection}-collection/collection/resource/{resource_hash}"
    else:
        raise ValueError(f"invalid stage {stage}")
