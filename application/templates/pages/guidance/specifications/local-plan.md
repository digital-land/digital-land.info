**Last updated: 3 April 2025**<br/>

---


There are 4 datasets you must provide for local plan data:

* Local plan dataset
* Local plan boundary dataset
* Local plan document dataset
* Local plan timetable dataset

### Format

You can provide data in one of these formats:

* CSV
* GeoJSON
* GML
* Geopackage

These may be uploaded to a single URL, or served via an OGC WFS or ArcGIS API.

### Field names
You can provide field names using hyphens, underscores or spaces.

For example:

* `start-date`
* `start_date`
* `start date`

These are all valid, and any uppercase characters will be converted to lowercase.

## Local plan dataset

This dataset is about local plans. Local plans are prepared by a local planning authority in consultation with its community to set out a vision and a framework for the development of an area. Don’t worry if you don’t have all the data we’ve asked for available right now. If you give us what you’ve got, we can help you fill in the gaps later.

A complete record should contain the following fields (columns):

### reference

A reference or ID for the local plan that is:

* unique within your dataset
* permanent - it doesn't change when the dataset is updated

If you don't use a reference already, you will need to create one. This can be a short set of letters or numbers.

Example: `Leeds-LP01`

### name

The official name of the local plan.

Example: `The Adopted Local Plan for Leeds`

### description

A brief description of the plan.

Example: `The new local plan will set out how Bristol will develop up to 2040`

### period-start-date

The start date of the period the plan covers.

Example: `2024-03-28`

With dates, some data is better than no data, so:

* `2024` is fine
* `2024-03` is better
* `2024-04-28` is brilliant

### period-end-date

The end date of the period the plan covers.

Example: `2030-03-28`

With dates, some data is better than no data, so:

* `2030` is fine
* `2030-03` is better
* `2030-04-28` is brilliant

### local-plan-boundary

The reference code for the boundary the plan covers - use the same one you are using for the reference field in your local-plan-boundary dataset.

Example: `YORK-LPB-01`

### documentation-url
The web page where you can find the documentation for the plan

Example
`http://www.LPAwebsite.org.uk/local-plan`

### organisations
The code for the organisation or organisations responsible for the local plan. If it’s more than one organisation, separate them with a comma.
Create this code by using the relevant prefix, a colon (:), and the reference for your organisation from this [list of organisations](https://www.planning.data.gov.uk/organisation/).

Example: `local-authority:BUC`

### entry-date

The date this information has been entered as a record.

Write in YYYY-MM-DD format.

Example: `2022-12-20`

With dates, some data is better than no data, so:

* `2022` is fine
* `2022-12` is better
* `2022-12-20` is brilliant

### start-date
The date the validity of the record starts, written in YYYY-MM-DD format.

Example: `2024-04-25`

With dates, some data is better than no data, so:

* `2024` is fine
* `2024-04` is better
* `2024-04-25` is brilliant

### end-date
The date the validity of the record ends, written in YYYY-MM-DD format.

Example: `2030-01-20`

With dates, some data is better than no data, so:

* `2030` is fine
* `2030-01` is better
* `2030-01-20` is brilliant

## Local plan boundary dataset

This dataset is about local plan boundaries. Don’t worry if you don’t have all the data we’ve asked for available right now. If you give us what you’ve got, we can help you fill in the gaps later.

A complete record should contain the following fields (columns):

### reference

A reference or ID for the boundary the plan covers. If it covers the exact planning authority boundary then use the planning authority boundary reference.

It must be:

* unique within your dataset
* permanent - it doesn't change when the dataset is updated

If you don't use a reference already, you will need to create one. This can be a short set of letters or numbers.

Example: `YORK-LPB-01`

### name

A name for the boundary.

Example: `City of York boundary`

### geometry

The boundary for the local plan as a single polygon or multipolygon value. All points in the polygon should be in the WGS84 coordinate reference system if possible. If you can’t do this, give us what you have and then we can transform it into WGS84. However, this could mean there’s a small loss of precision when we do the transformation. If you’re providing geometry in a CSV, geometry should be in well-known text (WKT).

Example: `MULTIPOLYGON (((1.188829 51.23478,1.188376 51.234909,1.188381 51.234917,1.187912 51.235022...`

If you’re providing geometry in a GeoJSON, GML or Geopackage, use the associated geometry format.

### description

A description of the boundary. Provide more detail if the boundary is different from the planning authority boundary.

Example: `The new local plan boundary covers Borchester City but also extends to include Borchester Park`

### organisations

The code for the organisation or organisations responsible for the local plan. If it’s more than one organisation, separate them with a comma.

Example: `local-authority:BUC`

Create this code by using the relevant prefix, a colon (:), and the reference for your organisation from this [list of organisations.](https://www.planning.data.gov.uk/organisation/)

### entry-date

The date this information has been entered as a record.

Write in YYYY-MM-DD format.

Example: `2022-12-20`

With dates, some data is better than no data, so:

* `2022` is fine
* `2022-12` is better
* `2022-12-20` is brilliant

### start-date

The date the validity of the record starts, written in YYYY-MM-DD format.

Example: `2024-04-25`

With dates, some data is better than no data, so:

* `2024` is fine
* `2024-04` is better
* `2024-04-25` is brilliant

### end-date

The date the validity of the record ends, written in YYYY-MM-DD format.

Example: `2030-01-20`

With dates, some data is better than no data, so:

* `2030` is fine
* `2030-01` is better
* `2030-01-20` is brilliant

## Local plan document dataset

This dataset is about local plan documents that form part of the local plan, or support it. Don’t worry if you don’t have all the data we’ve asked for available right now. If you give us what you’ve got, we can help you fill in the gaps later. You should add to this dataset every time you complete and publish a new document.

A complete record should contain the following fields (columns):

### reference

A reference or ID for the document that is:

* unique within your dataset
* permanent - it doesn't change when the dataset is updated

If you don't use a reference already, you will need to create one. This can be a short set of letters or numbers.

Example: `CORESTRAT-2017-08`

### name

The name of the document.

Example: `Borchester Core Strategy August 2017`

### description

A description of the document.

Example: `The core strategy is the main planning document which guides development choices and decisions in Borchester. The strategy was adopted on 10 August 2017`

### local plan

The reference you created for this particular local plan for the local plan dataset.

Example: `Leeds-LP01`

### document-type

The code for the type of document this record refers to. Find the code you need using this [finder tool.](https://dataset-editor.planning.data.gov.uk/dataset/local-plan-document-type/finder)

If you can’t see the code for the document type you need, let us know in this [GitHub discussion.](https://github.com/digital-land/data-standards-backlog/discussions/97)

Example: `sustainability-appraisal`

### documentation-url

The web page where you can find the documentation for the document.

Example: `http://www.LPAwebsite.org.uk/local-plan/core-strategy`

### document-url

The URL of the document file itself.

Example: `http://www.LPAwebsite.org.uk/local-plan/core-strategy/core-strategy-2017.pdf`

### organisations

The code for the organisation or organisations responsible for the local plan. If it’s more than one organisation, separate them with a comma.

Create this code by using the relevant prefix, a colon (:), and the reference for your organisation from this [list of organisations.](https://www.planning.data.gov.uk/organisation/)

Example: `local-authority:BUC`

### entry-date

The date this information has been entered as a record.

Write in YYYY-MM-DD format.

Example: `2022-12-20`

With dates, some data is better than no data, so:

* `2022` is fine
* `2022-12` is better
* `2022-12-20` is brilliant

### start-date

The date the validity of the record starts, written in YYYY-MM-DD format.

Example: `2024-04-25`

With dates, some data is better than no data, so:

* `2024` is fine
* `2024-04` is better
* `2024-04-25` is brilliant

### end-date

The date the validity of the record ends, written in YYYY-MM-DD format.

Example: `2030-01-20`

With dates, some data is better than no data, so:

* `2030` is fine
* `2030-01` is better
* `2030-01-20` is brilliant

## Local plan timetable dataset

This dataset is about local plan timetables. Don’t worry if you don’t have all the data we’ve asked for available right now. If you give us what you’ve got, we can help you fill in the gaps later.

If you’re in the early stages of making your local plan, we expect the dates you give us to be estimated to at least the nearest month in which you think the event will happen. When they actually happen we’d expect you to update the dataset with the actual date (YYYY-MM-DD).

You should update this dataset regularly as you update your estimates, if plans change and as events happen.

A complete record should contain the following fields (columns):

### reference

A reference or ID for the local plan timetable that is:

• unique within your dataset
• permanent - it doesn't change when the dataset is updated

If you don't use a reference already, you will need to create one. This can be a short set of letters or numbers.

Example: `LeedsLP-timetable01`

### name

The name of the local plan timetable.

Example: `The Adopted Local Plan for Leeds Timetable`

### local-plan
The reference you created for this particular local plan for the local plan dataset.

Example: `Leeds-LP01`

### local-plan-event

The code for the type of event this record refers to. Find the code you need using [this finder tool.](https://dataset-editor.planning.data.gov.uk/dataset/local-plan-event/finder)

Example: `estimated-plan-adoption-date`

### event-date

The date this event happened.

With dates, some data is better than no data, so:

* `2022` is fine
* `2022-12` is better
* `2022-12-20` is brilliant

### notes

Optional text on how this data was made or produced, or how it can be interpreted.

### organisation

The code for the organisation or organisations responsible for the local plan. If it’s more than one organisation, separate them with a comma.

Create this code by using the relevant prefix, a colon (:), and the reference for your organisation from this [list of organisations.](https://www.planning.data.gov.uk/organisation/)

Example: `local-authority:BUC`

### entry-date

The date this information has been entered as a record.

Write in YYYY-MM-DD format.

Example: `2022-12-20`

With dates, some data is better than no data, so:

* `2022` is fine
* `2022-12` is better
* `2022-12-20` is brilliant

### start-date

The date the validity of the record starts, written in YYYY-MM-DD format.

Example: `2024-04-25`

With dates, some data is better than no data, so:

* `2024` is fine
* `2024-04` is better
* `2024-04-25` is brilliant

### end-date

The date the validity of the record ends, written in YYYY-MM-DD format.

Example: `2030-01-20`

With dates, some data is better than no data, so:

* `2030` is fine
* `2030-01` is better
* `2030-01-20` is brilliant
