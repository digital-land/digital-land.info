There are 3 datasets you must provide for tree preservation orders:

- [tree preservation order dataset](#{{ 'tree preservation order dataset' | slugify }})
- [tree preservation zone dataset](#{{ 'tree preservation zone dataset' | slugify }})
- [tree dataset](#{{ 'tree dataset' | slugify }})

Format
------

The tree preservation order dataset should be provided as a CSV file.
You can provide the zone and individual tree data in one of these formats:

-   CSV
-   GeoJSON
-   GML
-   Geopackage

For more information, see [how to provide your data](../how-to-provide-data).

Tree preservation order dataset
-------------------------------

This dataset is about tree preservation orders (TPOs). These are orders made by local planning authorities to protect specific trees, groups of trees or woodlands.

The dataset must contain at least one entry (row) for each tree preservation order.

It must containing the following fields (columns):

### reference

A reference or ID for each tree preservation order that is:

-   unique within your dataset
-   permanent - it doesn't change when the dataset is updated

If you don't use a reference already, you will need to create one. This can be a short set of letters or numbers.

Example: `TPO1`

### name

This will be the title of the page hosting data about this tree preservation order on our website. This can be:

-   name
-   reference
-   address
-   blank

### document-url

The URL of an authoritative order or notice designating the tree preservation order.

Example: `http://www.LPAwebsite.org.uk/tpo1.pdf`

### documentation-url

The URL of the webpage citing the document.

Each document should be linked to on a documentation webpage that includes a short description of the data. The website URL should be unique for each tree preservation order, either by creating a separate page or a separate anchor (fragment identifier) for each one.

Example: `http://www.LPAwebsite.org.uk/data#tpo1`

### notes

Optional text on how this data was made or produced, or how it can be interpreted.

### start-date

The date that the tree preservation order came into force, written in `YYYY-MM-DD` format.

Example: `1984-03-28`

### end-date

If applicable, the date that the tree preservation order was no longer in effect, written in `YYYY-MM-DD` format. If it's still in effect, leave the cell blank.

Example: `1999-01-20`

### entry-date

The date this dataset was created or last updated, written in `YYYY-MM-DD` format.

Example: `2022-12-20`

### made-date

The date a tree preservation order was "made". From this date the included tree(s), from a planning perspective, are considered to be covered by a tree preservation order.

Example: `2022-12-20`

### confirmed-date

The date a tree preservation order is confirmed and becomes a fully fledged tree preservation order.

Example: `2022-12-20`

---

Tree preservation zone dataset
------------------------------

This dataset is about tree preservation zones. These are areas of trees that are under a tree preservation order. You may also know them as tree preservation
zones or groups.

The dataset must contain at least one entry (row) for each tree preservation zone.

It must containing the following fields (columns):

### reference

A reference or ID for each tree preservation zone that is:

-   unique within your dataset
-   permanent - it doesn't change when the dataset is updated

If you don't use a reference already, you will need to create one. This can be a short set of letters or numbers.

Example: `TPO1`

### name

This will be the display name of the page hosting data about this tree preservation zone on our website. This can be:

-   name
-   reference
-   address
-   blank

### tree-preservation-order

The reference for the tree preservation order that covers this zone.

### tree-preservation-zone-type

A category of tree preservation zone

### geometry

The boundary for the tree preservation zone as a single polygon or multipolygon value. All points in the polygon must be in the WGS84 coordinate reference system.

If you’re providing geometry in a CSV, geometry should be in well-known text (WKT).

Example:
`MULTIPOLYGON (((1.188829 51.23478,1.188376 51.234909,1.188381 51.234917,1.187912 51.235022...`

If you’re providing geometry in a GeoJSON, GML or Geopackage, use the associated geometry format.

### notes

Optional text on how this data was made or produced, or how it can be interpreted.

### start-date

The date that the tree preservation order came into force, written in `YYYY-MM-DD` format.

Example: `1984-03-28`

### end-date

If applicable, the date that the tree preservation order was no longer in effect, written in `YYYY-MM-DD` format. If it's still in effect, leave the cell blank.

Example: `1999-01-20`

### entry-date

The date this dataset was created or last updated, written in `YYYY-MM-DD` format.

Example: `2022-12-20`

---

Tree dataset
------------

This dataset is about trees. These are individual trees that are under a tree preservation order.

The dataset must contain at least one entry (row) for each tree.

It must containing the following fields (columns):

### reference

A reference or ID for each tree that is:

-   unique within your dataset
-   permanent - it doesn't change when the dataset is updated

If you don't use a reference already, you will need to create one. This can be a short set of letters or numbers.

Example: `T1`

### name

This will be the title of the page hosting data about this tree preservation order on our website. This can be:

-   name
-   reference
-   address
-   blank

### point

The approximate location of the centre of the tree.

You must provide a point or geometry for each tree. You may provide both.

### tree-preservation-order

The reference for the tree preservation order that affects this tree.

Example: `TPO1`

### geometry

The boundary of the tree as a single polygon or multipolygon value. All points in the polygon must be in the WGS84 coordinate reference system.

If you’re providing geometry in a CSV, geometry should be in well-known text (WKT).

You must provide a point or geometry for each tree. You may provide both.

Example:
`MULTIPOLYGON (((1.188829 51.23478,1.188376 51.234909,1.188381 51.234917,1.187912 51.235022...`

If you’re providing geometry in a GeoJSON, GML or Geopackage, use the associated geometry format.

### uprn

If the tree has one, you can provide the Unique Property Reference Number (UPRN). [Find the UPRN on GeoPlace](https://www.geoplace.co.uk/addresses-streets/location-data/the-uprn).

If you provide the UPRN, you must also provide the address text.

### address-text

If the tree has one, you can provide the address, written as text.

If you provide the address text, you must also provide the UPRN.

Example: `100 High Street, Bath`

### notes

Optional text on how this data was made or produced, or how it can be interpreted.

### start-date

The date from which the tree preservation order affects the tree, written in `YYYY-MM-DD` format.

Example: `1984-03-28`

### end-date

If applicable, the date from which the tree preservation order no longer affects the tree, written in `YYYY-MM-DD` format. If it's still in effect, leave the cell blank.

Example: `1999-01-20`

### entry-date

The date this dataset was created or last updated, written in `YYYY-MM-DD` format.

Example: `2022-12-20`

---

Go to [how to provide your data](../how-to-provide-data).
