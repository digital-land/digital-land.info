There are 2 datasets you must provide for design codes:

- [design code dataset](#{{ 'design code dataset' | slugify }})
- [design code area dataset](#{{ 'design code area dataset' | slugify }})

_The datasets may be provided as a single file by adding the geometry field to the design code dataset, or as two separate files._

Format
------

The design code dataset should be provided as a CSV file.
You can provide the area data in one of these formats:

-   CSV
-   GeoJSON
-   GML
-   Geopackage

For more information, see [how to provide your data](../how-to-provide-data).

Design code dataset
-------------------

This dataset is a list of design codes. These are policies made by local planning authorities to describe design codes which reflect local character and design preferences for buildings.

The dataset must contain at least one entry (row) for each design code document.

It must containing the following fields (columns):

### reference

A reference or ID for each design code that is:

-   unique within your local planning authority dataset
-   permanent - it doesn't change when the dataset is updated

If you don't use a reference already, you will need to create one. This can be a short set of letters or numbers.

Example: `DCO1`

### name

This will be the title of the design code displayed on our website.

Example: `Design of chimneys in Borchester`

### document-url

The URL of the HTML, PDF or other document documenting the design code.

Example: `http://www.borchester.gov.uk/document/dc01.pdf`

### documentation-url

The URL of the webpage citing the design code document.

Each document should be linked to on a documentation webpage that includes a short description of the design code.
The website URL should be unique for design code, either by creating a separate page or a separate anchor (fragment identifier) for each design code.

Example: `http://www.borchester.gov.uk/design-codes#dc01`

### design-code-area

The reference of the design code area where this design code applies.

### notes

Optional text on how this data was made or produced, or how it can be interpreted.

### start-date

The date that the design code came, or comes into force, written in `YYYY-MM-DD` format.

Example: `1984-03-28`

### end-date

If applicable, the date that the design code was no longer in effect, written in `YYYY-MM-DD` format. If it's still in effect, leave the cell blank.

Example: `1999-01-20`

### entry-date

The date this dataset was created or last updated, written in `YYYY-MM-DD` format.

Example: `2022-12-20`

---

Design code area dataset
------------------------

This dataset is about the geographical area where each design code applies.

The dataset must contain at least one entry (row) for design code area.

It must containing the following fields (columns):

### reference

A reference or ID for each design code area that is:

-   unique within your dataset
-   permanent - it doesn't change when the dataset is updated

If you don't use a reference already, you will need to create one. This can be a short set of letters or numbers.
The design code area may have the same reference as the design code.

Example: `DC01`

### name

This will be the display name of the page hosting data about this design code area on our website.

Example: `Felpersham town centre design code area`

### geometry

The boundary for the design code area as a single polygon or multipolygon value. Points must be in the WGS84 coordinate reference system.

This should be in GeoJSON format.

Example:
`MULTIPOLYGON (((1.188829 51.23478,1.188376 51.234909,1.188381 51.234917,1.187912 51.235022...`

### notes

Optional text on how this data was made or produced, or how it can be interpreted.

### start-date

The date that the design code came into force, written in `YYYY-MM-DD` format.

Example: `1984-03-28`

### end-date

If applicable, the date that the design code area was no longer in effect, written in `YYYY-MM-DD` format. If it's still in effect, leave the cell blank.

Example: `1999-01-20`

### entry-date

The date this dataset was created or last updated, written in `YYYY-MM-DD` format.

Example: `2022-12-20`

---

Go to [how to provide your data](../how-to-provide-data).
