Publish your data
--------------------

You must publish your data:

- on a webpage on your official planning authority's website - which usually ends in **gov.uk**
- in a format that is clear and easy to understand

Provide your data
--------------------

After you publish, you should provide your data to the Planning Data Platform.

You need to submit:

- your full name
- your work email address
- the URL where anyone can download your data - called your **endpoint URL**
- the URL for your **gov.uk** website where you can view or select a link to view the data - called your **source webpage URL**

Each URL must be:

- accessible to the public
- hosted on a server that does not block access due to set permissions

We automatically collect the latest data from your endpoint URL every day, you do not need to provide anything again.

Your local planning authority is the source of truth for the data.

Hosting your data
--------------------

Endpoints are usually either a:

- file hosted on your web server - like URLs that end in **.json** or **.csv**
- live data feed from an API - hosted by your Geographic Information System (GIS) software or open data platform

<details class="govuk-details">
  <summary class="govuk-details__summary">
    <span class="govuk-details__summary-text">
      Help with providing data using an ArcGIS link
    </span>
  </summary>
  <div class="govuk-details__text">
    <p class="govuk-body">An ArcGIS data layer URL usually looks like this:</p>
    <p class="govuk-body"><code>https://maps.example.gov.uk/arcgis/rest/services/Planning/LocalPlans/FeatureServer/0</code></p>
    <p class="govuk-body">This URL is made up of:</p>
    <ul class="govuk-list govuk-list--bullet">
      <li>the organisation's website (maps.example.gov.uk)</li>
      <li>the ArcGIS REST services path (/arcgis/rest/services)</li>
      <li>the name of the service (Planning/LocalPlans)</li>
      <li>the type of service (for example FeatureServer or MapServer)</li>
      <li>a number that identifies the layer within the service (/0)</li>
    </ul>
  </div>
</details>

You only need to make changes to your data at your endpoint URL. Do not change your endpoint URL when you make updates.

Create your webpage
--------------------

The webpage must include, for each dataset:

- the link to the endpoint URL
- a summary of what the data is about
- a statement that the data is provided under the [Open Government Licence](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)

Within your endpoint, you will need a `documentation-url` for each record in your dataset.

The `documentation-url` is the URL of the specific section of your webpage that introduces each record - for example, a particular Article 4 Direction or conservation area. Each record must have its own unique URL.

There are two ways to do this:

- **One page per record**: each record has its own webpage. The URL for each record is its full-page URL, for example `yourwebsite.gov.uk/planning/article-4-directions/smith-road`.
- **Multiple records on one page**: all records are listed on a single page, with an anchor link for each one, for example `yourwebsite.gov.uk/planning/article-4-directions#smith-road`. Your publishing system will need to support anchor links (fragment identifiers) for each record.

Where your data includes a link to a legal document such as a direction notice or order, you should also provide a `document-url` pointing directly to that file.

See [example webpages showing how to publish planning data](https://digital-land.github.io/documentation-url-examples/) for patterns you can follow, including examples of how the `documentation-url` works for each approach.
