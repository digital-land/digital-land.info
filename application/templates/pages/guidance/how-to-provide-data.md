The Planning Data platform gathers data from local planning authorities (LPAs) across England. We do this in order to make the data more open and accessible, so better planning decisions are made.

This guidance will take you through the process of publishing data that meets the technical specifications required by the Planning Data platform.

---

## Steps

1.  [Prepare your data](#{{ 'Step 1: Prepare your data' | slugify }})

2.  [Provide your documentation](#{{ 'Step 2: Provide your documentation' | slugify }})

3.  [Create or update the webpage hosting your data](#{{ 'Step 3: Create or update the webpage hosting your data' | slugify }})

4.  [Tell Planning Data where the webpage is](#{{ 'Step 4: Tell Planning Data where the webpage is' | slugify }})

---

Step 1: Prepare your data
-------------------------------------

The data needed for the Digital Planning Services such as [PlanX](https://opendigitalplanning.org/services) are:

-   [Article 4 direction data](specifications/article-4-direction)
-   [Conservation area data](specifications/conservation-area)
-   [Listed building data](specifications/listed-building)
-   [Tree preservation order data](specifications/tree-preservation-order)

You may need to create more than one set of data for each subject. You'll find what to include in the [data specifications guidance](specifications/).

We will accept data supplied as either:

-   CSV
-   GeoJSON
-   GML
-   Geopackage

These may be uploaded to a single URL, or served via an OGC WFS or ArcGIS API.

It’s important that the data used in Digital Planning Services is as up to date as possible - whatever data you provide us with must be maintained and updated to reflect changes in your planning constraints.

---

Step 2: Provide your documentation
----------------------------------

For most data subjects, you must also publish links to supporting documentation that gives evidence that the data is correct.

See the [data specifications guidance](specifications/) for how to provide this for each different subject.

We have preferred formats for each field. We automatically change the formats of some fields, for example the dates.

---

Step 3: Create or update the webpage hosting your data
------------------------------------------------------

To complete step 3, you must be able to edit a webpage on your LPA's official website. This will probably have a URL ending in .gov.uk or .org.

If you aren't able or authorised to do this, please speak to a person who updates your organisation's website.

### Create a webpage

Create a separate webpage for each dataset. This webpage must have a URL that does not change, so the Planning Data platform can keep collecting the data.

If the URL does change, please email <digitalland@levellingup.gov.uk>.

You may want to use an alias to create a short URL that is easy to remember. For example: https://www.yourLPA.gov.uk/conservation-area-data

### Describe the data

Add a short description of the data on the page. We recommend including these descriptors as a minimum:

**Summary**

Briefly explain what the data is about. For example:

This dataset shows the locations of conservation areas. Conservation areas are designated to safeguard areas of special architectural and historic interest, the character and appearance of which it is desirable to preserve or enhance. Within these areas special planning controls operate which need to be considered when undertaking development.

**Licensing**

State that the data is provided under the [Open Government Licence](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).

**Last updated**

The date you are creating or updating the webpage.

**Link to your data**

Publish the links to your data on this page. Depending on what format you supply the data in, this could be the uploaded CSV, GeoJSON or GML files, or the link to the OGC WFS service.

---

Step 4: Tell Planning Data where the webpage is
-----------------------------------------------

If you are creating a new webpage, you must tell us the URL. Email the URL of the webpage containing your files to <digitalland@levellingup.gov.uk>.

If you have already told us, you can skip this step. The Planning Data platform will regularly collect data from the URL you have given us.

If the URL ever changes, please tell us.
