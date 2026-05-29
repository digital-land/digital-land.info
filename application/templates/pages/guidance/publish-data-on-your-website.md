You must publish your data:

- on a webpage on your official planning authority's website - which usually ends in **gov.uk**
- in a format that is clear and easy to understand

You can publish your data using any of the following:

- CSV
- GeoJSON
- GML
- GeoPackage

You must include a statement to confirm that you provided the data under the [Open Government Licence](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).

[Find out mopre about how to publish data on your website.](https://digital-land.github.io/documentation-url-examples/)

## Hosting your data
An enpoint URL is where anyone can download your data

Endpoints are usually either a:

- file hosted on your web server - like URLs that end in **.json** or **.csv**
- live data feed from an API - hosted by your Geographic Information System (GIS) software or open data platform

Help with providing data using an ArcGIS data layer
An ArcGIS data layer URL usually looks like this:

`https://maps.example.gov.uk/arcgis/rest/services/Planning/LocalPlans/FeatureServer/`

This URL is made up of:

- the organisation's website (maps.example.gov.uk)
- the ArcGIS REST services path (/arcgis/rest/services)
- the name of the service (Planning/LocalPlans)
- the type of service (for example FeatureServer or MapServer)
-      a number that identifies the layer within the service (/0)

You only need to make changes to your data at your endpoint URL. Do not change your endpoint URL when you make updates.

## Create your webpage

For each dataset, your webpage must include a:

- the link to the endpoint URL
- a summary of what the data is about
- a statement that the data is provided under the [Open Government Licence](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)

Within your endpoint, you will need a `documentation-url` for each record in your dataset.

### Give each record a documentation-URL

Each record in your dataset needs a `documentation-url` so that we can find the part of your webpage that includes the record.

Each documentation-URL must be unique. There are 2 ways that you can create a unique URL.


1. **One page per record** <br>Give each record has its own webpage so that the documentation-url is the full page address. For example `yourwebsite.gov.uk/planning/article-4-directions/smith-road`.</br>

2. **Multiple records on one page** <br>List all records on a single page and add anchor link for each one, for example `yourwebsite.gov.uk/planning/article-4-directions#smith-road`.</br>

You need to check that your publishing system supports anchor links (fragment identifiers).


### Legal documents
If a record is for a legal document. you need to add a `document-url` that links straight to the file. For example, a direction notice or order.

### Examples
[View example webpages showing how to publish planning data.](https://digital-land.github.io/documentation-url-examples/)
