Before you provide your data, you must publish your data on a webpage on your official planning authority website, usually ending in gov.uk. Your local planning authority will always be the source of truth about your data.

Your data must be on a URL the public can access. We collect the latest data from there every day. We call this the ‘endpoint URL’.

You must link to your endpoint URL from your webpage URL.

Endpoints typically fall into 1 of the following 2 categories:

- a file hosted on your web server — these will usually be URLs which end in something like .json or .csv
- a live feed of the data from an API — these are usually hosted by your GIS (Geographic Information System) software or open data platform

Whenever your data changes, update it in the endpoint URL. Your endpoint URL must remain the same, do not change it when you make updates.

Create your webpage
--------------------

The webpage must include, for each dataset:

- the link to the endpoint URL
- a summary of what the data is about
- a statement that the data is provided under the [Open Government Licence](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)

Within your endpoint, you will need a `documentation-url` for each record in your dataset.

The `documentation-url` is the URL of the specific section of your webpage that introduces each record - for example, a particular Article 4 Direction or conservation area. Each record must have its own unique URL.

There are two ways to do this:

- **One page per record**: each record has its own webpage. The URL for each record is its full page URL, for example `yourwebsite.gov.uk/planning/article-4-directions/smith-road`.
- **Multiple records on one page**: all records are listed on a single page, with an anchor link for each one, for example `yourwebsite.gov.uk/planning/article-4-directions#smith-road`. Your publishing system will need to support anchor links (fragment identifiers) for each record.

Where your data includes a link to a legal document such as a direction notice or order, you should also provide a `document-url` pointing directly to that file.

See [example webpages showing how to publish planning data](https://digital-land.github.io/documentation-url-examples/) for patterns you can follow, including examples of how the `documentation-url` works for each approach.
