import csv
import logging
from collections import defaultdict
from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from typing import Optional

from digital_land.view_model import JSONQueryHelper, DigitalLandModelJsonQuery

from ..data_store import DataStore, get_datastore, organisation
from ..resources import templates

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_class=HTMLResponse)
def resource_index(
    request: Request, 
    page: Optional[int] = 1):
    paging = DigitalLandModelJsonQuery().get_paging(key="resource", table="resource")["rows"]

    if page < 1 or page > len(paging) + 1:
        raise HTTPException(status_code=404, detail="Resources not found")

    start_resource = paging[page-2]["resource"] if page > 1 else "0"
    
    resp = DigitalLandModelJsonQuery().get_resources(start_resource)
    resources = resp["rows"]

    return templates.TemplateResponse(
        "index.html", {
            "request": request, 
            "collection": {}, 
            "resources":  resources, 
            "paging" : {
                "current_page": page,
                "total_pages": len(paging) + 1
            }
        }
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
    resource_data = DigitalLandModelJsonQuery().fetch_resource_info(resource_hash)[
        "rows"
    ]
    if len(resource_data) == 0:
        raise HTTPException(status_code=404, detail="Resource not found")

    payload["resource"] = resource_hash

    # TODO Sanity check this logic... taking arbitrary items from a list makes me nervous
    #      Maybe we should return a list of collections?
    # collection_name = collection.source.records[resource_endpoints[0]][0]["collection"]
    payload["collections"] = [endpoint["collections"] for endpoint in resource_data]
    collection_name = payload["collections"][0]

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
    for e in resource_data:
        organisations = []
        orgs_seen = set()
        for org in e["organisations"].split(","):
            if not org or org in orgs_seen:
                continue
            organisations.append(
                {"name": organisation.organisation[org]["name"], "id": org}
            )

        endpoints.append(
            {
                "endpoint_url": e["endpoint_url"],
                "organisations": organisations,
                "start_date": format_date(e["first_collection_date"]),
                "last_collected": format_date(e["last_collection_date"]),
            }
        )

    payload["endpoints"] = endpoints

    files = []
    # Collected
    files.append(
        {
            "name": "Collected",
            "format": "UNKNOWN",
            "size": "{:,.2f} KB".format(int(resource_data[0]["bytes"]) / 1024),
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
