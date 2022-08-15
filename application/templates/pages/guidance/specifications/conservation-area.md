There are 2 datasets you must provide for conservation area data:

- [conservation area dataset](#{{ 'conservation area dataset' | slugify }})
- [conservation area document dataset](#{{ 'Conservation area documents dataset' | slugify }})

Format
------

You can provide data in one of these formats:

-   CSV
-   GeoJSON
-   GML
-   Geopackage

For more information, see [how to provide your data](../how-to-provide-data).

Conservation area dataset
-------------------------

This dataset is about conservation areas. These are areas where extra planning controls apply due to their special architectural and historic interest.

The dataset must contain at least one entry (row) for each conservation area.

It must containing the following fields (columns):

### reference
A reference or ID for each conservation area that is:

-   unique within your dataset
-   permanent - it doesn't change when the dataset is updated

If you don't use a reference already, you will need to create one. This can be a short set of letters or numbers.

Example: `CA01`

### name

The official name of the conservation area.

Example: `Old Market`

### geometry

The boundary for the conservation area as a single polygon or multipolygon value. Points must be in the WGS84 coordinate reference system.

This should be in GeoJSON format.

Example: `MULTIPOLYGON (((1.188829 51.23478,1.188376 51.234909,1.188381 51.234917,1.187912 51.235022...`

### documentation-url

An optional URL of a document providing the authoritative source of the boundary. For example, a PDF containing a map of the area, indicated with a red-line boundary.

### notes

Optional text on how this data was made or produced, or how it can be interpreted.

### start-date

The date that the conservation area was officially designated, written in `YYYY-MM-DD` format.

Example: `1984-03-28`

### end-date

If applicable, the date that the conservation area was no longer in effect, written in `YYYY-MM-DD` format. If this does not apply, leave the cell blank.

Example: `1999-01-20`

### entry-date

The date this dataset was created or last updated, written in `YYYY-MM-DD` format.

Example: `2022-12-20`

## Conservation area documents dataset

This dataset is about documents that provide sources for the information contained in the conservation areas dataset.  If you can, you should provide this dataset in addition to the conservation area dataset.

If your conservation area documents are all held in a single page, you add the URL of that page in the conservation area dataset instead of providing a separate conservation area documents dataset. Add the URL in the `documentation-url` field.

These documents are the authoritative source and provide the context around the history and impact of the conservation area. They can be:

-   draft directions
-   area appraisals
-   notices of conservation area designations
-   management plans
-   gazette entries

The dataset must contain at least one entry (row) for each conservation area document.
It must containing the following fields (columns):

### reference
A reference or ID for each document that is:

- unique within your dataset
- permanent - it doesn't change when the dataset is updated

If you don't use a reference already, you will need to create one. This can be a short set of letters or numbers.
Example: `CADOC01`

### name
The title of the document.
Example: `Notice of Old Market conservation area designation`

### conservation-area
The reference for the conservation area this document refers to, as used in the conservation area dataset.
Example: `CA1`

### documentation-url
The URL of the webpage citing the document.

Each document should be linked to on a documentation webpage that includes a short description of the data. The website URL should be unique for each conservation area, either by creating a separate page or a separate anchor (fragment identifier) for each one.

Example: `http://www.LPAwebsite.org.uk/data#conservationarea1`

### document-url
The URL of the document.
Example: `http://www.LPAwebsite.org.uk/conservationarea1.pdf`

### document-type
The type of document. This must be one of the following values, or left blank:

-   area-appraisal
-   notice

### notes

Optional text on how this data was made or produced, or how it can be interpreted.

### start-date
The date the document was published, written in `YYYY-MM-DD` format.
Example: `1984-03-28`

### end-date
The date the document was withdrawn or superseded by another document, written in `YYYY-MM-DD` format. Leave this blank if the document is still relevant to planning.
Example: `1984-03-28`

### entry-date
The date this entry was created or updated, written in `YYYY-MM-DD` format.
Example: `1984-03-28`

---

Go to [how to provide your data](../how-to-provide-data).
