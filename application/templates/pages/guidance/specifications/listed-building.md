**Last updated: 7 August 2025**<br/>

---

Presumption to publish
----------------------
Ordnance Survey has confirmed that our assessment of this dataset is correct, provided the data meets our specification.

[Read more about presumption to publish.](https://www.ordnancesurvey.co.uk/customers/public-sector/public-sector-licensing/publish-derived-data)

[View the discussion on Github.](https://github.com/digital-land/data-standards-backlog/discussions/44)

---

You must provide one dataset for listed buildings.

Format
------

You can provide data in one of these formats:

-   CSV
-   GeoJSON
-   GML
-   Geopackage

These may be uploaded to a single URL, or served via an OGC WFS or ArcGIS API.

## Field names

You can provide fields names using hyphens, underscores or spaces.

For example:

* `start-date`
* `start_date`
* `start date`

These are all valid, and any uppercase characters will be converted to lowercase.

Listed building outline dataset
------------------------

This dataset is about buildings listed on the National Heritage List for England because of their historical or architectural importance.

The dataset must contain at least one entry (row) for each listed building.

It must containing the following fields (columns):

### reference

A reference or ID for each listed building that is:

-   unique within your dataset
-   permanent - it doesn't change when the dataset is updated

If you don't use a reference already, you will need to create one. It can be the Historic England reference used in the [register of listed buildings](https://historicengland.org.uk/listing/the-list/), or a short set of letters or numbers.

Example: `LB1`

### name

The name of the listed building, as listed in the [register of listed buildings](https://historicengland.org.uk/listing/the-list/).

Example: `10 and 12, Lower Clapton Road E5`

### geometry

The listed building and any related area geometry as a single polygon or multipolygon value. Use [curtilage](https://historicengland.org.uk/images-books/publications/listed-buildings-and-curtilage-advice-note-10/) (according to the Historic England advice note) if it’s available. This is the boundary of the area to be considered for planning purposes. All points in the polygon must be in the WGS84 coordinate reference system.

If you’re providing geometry in a CSV, geometry should be in well-known text (WKT).

Example: `MULTIPOLYGON (((1.188829 51.23478,1.188376 51.234909,1.188381 51.234917,1.187912 51.235022...`

If you’re providing geometry in a GeoJSON, GML or Geopackage, use the associated geometry format.

### listed-building

The Historic England listed building reference for the listed building. This is recorded in the [register of listed buildings](https://historicengland.org.uk/listing/the-list/) as "List Entry Number".

Example: `1480524`

### uprns

The unique property reference number or numbers, separated by a comma, if the listing covers more than one. 

Example: `00021437334`

### description

Description of the location/setting of the listing.

Example: `Small chapel located in the west of Chapel Woods`

### notes

Optional text on how this data was made or produced, or how it can be interpreted.

### start-date

The date from which the building was listed, written in `YYYY-MM-DD` format.

Example: `1984-03-28`

### end-date

Where the building is [no longer listed](https://standards.planning-data.dev/principles/#we-shouldn%E2%80%99t-delete-entries-in-a-register), this should be the date that it was no longer in effect, written in `YYYY-MM-DD` format. If it's still listed, leave the cell blank.

Example: `1999-01-20`

### entry-date

The date the entity was last updated.

If the entity has never been updated, enter the same date as start-date.

Write in `YYYY-MM-DD` format.

Example: `2022-12-20`

---

### Technical specification

[Listed building outline technical specification](https://digital-land.github.io/specification/specification/listed-building/).

