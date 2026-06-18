
## Prepare your data

Your data does not need to be complete or perfect to start. You can start with what you have and improve it over time.

1. [Find your organisation](./Find your organisation).
2. Select the dataset that is relevant to your plan. For example, 'local plan'.

If we have data from alternative sources, you can download it from your dataset details page to help you get started.

### Datasets

The service currently supports:

- [article 4 directions](./article-4-direction)
- [brownfield land](https://www.gov.uk/government/publications/brownfield-land-registers-data-standard/publish-your-brownfield-land-data)
- [conservation areas](./conservation-area)
- [developer contributions](https://www.gov.uk/guidance/publish-your-developer-contributions-data)
- [infrastructure funding statements](https://digital-land.github.io/specification/specification/infrastructure-funding-statement/)
- [listed buildings](./listed-building)
- [plans including local plans, supplementary plans and minerals and waste plans](https://www.gov.uk/government/publications/publish-your-plan-data/publish-your-plan-data)
- [tree preservation orders](./tree-preservation-order)

We are currently testing and developing data standards for [design codes.](./design-code)

## Check your data

[Check your data](https://provide.planning.data.gov.uk) to find out if it is ready to publish or if you need to make any changes.

When your data is ready, you can publish it on your website.

You can check your data using any of the following:

- CSV
- GeoJSON
- GML
- GeoPackage
- the URL where anyone can download your data - called your 'endpoint URL'

## Publish your data

You must publish your data:

- on a webpage on your official planning authority's website - which usually ends in **gov.uk**
- in a format that is clear and easy to understand

You can publish your data using any of the following:

- CSV
- GeoJSON
- GML
- GeoPackage

You must include a statement to confirm that you provided the data under the [Open Government Licence](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).

[Find out more about how to publish data on your website.](https://digital-land.github.io/documentation-url-examples/)

### Hosting your data

An endpoint URL is where anyone can download your data.

Endpoints are usually either a:

- file hosted on your web server - like URLs that end in **.json** or **.csv**
- live data feed from an API - hosted by your Geographic Information System (GIS) software or open data platform

<details class="govuk-details">
  <summary class="govuk-details__summary">
    <span class="govuk-details__summary-text">
Help with providing data using an ArcGIS data layer
    </span>
  </summary>
  <div class="govuk-details__text">
    <p class="govuk-body">An ArcGIS data layer URL usually looks like this:</p>
    <p class="govuk-body"><code style="word-break: break-all;">https://maps.example.gov.uk/arcgis/rest/services/Planning/LocalPlans/FeatureServer/0</code></p>
    <p class="govuk-body">This URL is made up of:</p>
    <ul class="govuk-list govuk-list--bullet">
      <li>the organisation's website (maps.example.gov.uk)</li>
      <li>the ArcGIS REST services path (/arcgis/rest/services)</li>
      <li>the name of the service (Planning/LocalPlans)</li>
      <li>the type of service (for example FeatureServer or MapServer)</li>
      <li>a number that identifies the layer within the service (/0)</li>
    </ul>
  </div>
</details>

You only need to make changes to your data at your endpoint URL. Do not change your endpoint URL when you make updates.

### Create your webpage

For each dataset, your webpage must include a:

- link to the endpoint URL
- summary of what the data is about
- statement that the data is provided under the [Open Government Licence](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)

Within your endpoint, you will need a `documentation-url` for each record in your dataset.

### Give each record a documentation-URL

Each record in your dataset needs a `documentation-url`, so that we can find the part of your webpage that includes the record.

Each documentation-URL must be unique. There are 2 ways that you can create a unique URL.

1. **One page per record** <br>Give each record its own webpage, so that the documentation-url is the full page address. For example, [www.yourwebsite.gov.uk/planning/article-4-directions#smith-road](www.yourwebsite.gov.uk/planning/article-4-directions#smith-road).</br>

2. **Multiple records** <br>List all records on a single page and add anchor link for each one. For example, [www.yourwebsite.gov.uk/planning/article-4-directions#smith-road](www.yourwebsite.gov.uk/planning/article-4-directions#smith-road).</br>

You need to check that your publishing system supports anchor links (also called fragment identifiers).

### Legal documents

If a record is for a legal document, you need to add a `document-url` that links straight to the file. For example, a direction notice or order.

### Examples

[View example webpages that show how to publish planning data.](https://digital-land.github.io/documentation-url-examples/)

## Provide your data

After you publish, you should [provide your data to the Planning Data Platform.](https://provide.planning.data.gov.uk)

You need to submit:

- your full name
- your work email address
- the URL where anyone can download your data - called your 'endpoint URL'
- the URL for your gov.uk website where you can view or select a link to view the data - called your 'source webpage URL'

Providing your data will help to:

- maintain and improve your data quality
- make land and housing data easier to find, use and trust

## View your data

[Visit your organisation's dashboard](https://provide.planning.data.gov.uk) anytime to view the data you have provided and the datasets you still need to provide.

If there are any issues with your data after you provide it, we will let you know what you can do to improve it.

## Update your data

If you use the check and provide your data service, you only need to make changes to your data at your endpoint URL.
Planning.data.gov.uk will update automatically.

If you create a new endpoint URL, you will need to provide your data again.

## The Open Digital Planning community

If you’re part of the Open Digital Planning community, we expect you to submit the datasets that the service currently supports. [Read more about what’s expected of you](https://opendigitalplanning.org/digital-planning-improvement).

If you’re a local planning authority who is interested in becoming a member, you can [join the community](https://opendigitalplanning.org/join).

## Get Help

If you need any help at any stage of the process, let us know by emailing [digitalland@communities.gov.uk](mailto:digitalland@communities.gov.uk) and a member of our team will be in touch.
