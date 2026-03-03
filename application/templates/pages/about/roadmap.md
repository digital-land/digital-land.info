This roadmap shows our current plans for making it easier to find, use and trust planning and housing data.

We work in 3-month cycles and we aim to update this roadmap every 3 months. Our plans can change based on what we learn from speaking to our users, testing iterations, and how we can better deliver on our mission.

Last updated 3 March 2026. Next update due June 2026.

## Designing data

We are designing and collecting data that is valuable to housing and planning, and improving the quantity of [data on the platform](https://www.planning.data.gov.uk/dataset/).

We regularly ask our community to help us decide the things we need to work on and tell us what they need from the data. See [how you can contribute](https://design.planning.data.gov.uk/how-to-contribute) and [get an existing dataset onto planning.data.gov.uk](https://design.planning.data.gov.uk/how-to-get-existing-datasets-on-to-planning-data-gov-uk).

### Now

- We are also working with an [advisory group](https://design.planning.data.gov.uk/advisory-group) to develop a set of open, reusable data specifications to underpin planning applications.
- We are continuing to add [local plan boundaries, documents and timetables](https://www.planning.data.gov.uk/entity/?dataset=local-plan-boundary&dataset=local-plan-document&dataset=local-plan-timetable&entry_date_day=&entry_date_month=&entry_date_year=) to the platform.
- We are making it easier for data consumers and planning policymakers to get involved in our [data design process](https://design.planning.data.gov.uk/data-design-process). We are also taking more data specifications related to local planning through the [Screen and Research stages](https://design.planning.data.gov.uk/planning-consideration/?stage=Screen&stage=Research&stage=%5B%27screen%27%5D) of our process.
- Based on our [data quality framework](https://digital-land.github.io/technical-documentation/data-operations-manual/Explanation/Key-Concepts/Data-quality-needs/#measuring-data-quality), we’re introducing checks and changes to data management processes that will ensure the accuracy, consistency, and integrity of all datasets.

### Next

- We will be adding more datasets needed by the Planning Inspectorate and nationally significant infrastructure projects (consultees and geographies).
- We will draft a template Statutory Instrument for potential data standards.
- We will make it possible for local planning authorities to provide planning applications and decisions through our service.

### Later

- We will support the rollout of planning application submission and decision specifications.
- We will be adding further datasets as required to support emerging and existing planning legislation and guidance.

## Collecting and managing data

We are supporting local planning authorities across England to help them provide planning and housing data through our platform. Through the [Open Digital Planning community](https://opendigitalplanning.org/community-members), we’re supporting over 200 Local Planning Authorities (LPAs) to publish data, improve its quality and adopt digital planning products such as [PlanX](https://opendigitalplanning.org/services) and [BoPS](https://bops.digital). Alongside this, we are ensuring that our data collection pipeline remains performant as we grow the amount of data that we collect, standardise and index each night.

We are also developing Extract in partnership with the [Incubator for AI](https://ai.gov.uk/) ([Department of Science, Innovation and Techology](https://www.gov.uk/government/organisations/department-for-science-innovation-and-technology)) - an AI tool that [unlocks historical planning data from documents](https://mhclgdigital.blog.gov.uk/2025/06/12/extract-using-ai-to-unlock-historic-planning-data/), reducing the effort for LPAs to provide standardised data and increasing the amount of trusted data on the platform. 

### Now

- We are making it faster and more reliable to build and rebuild planning data. Our platform can now be refreshed in hours rather than days, giving users quicker access to up-to-date, authoritative information. This work has also allowed us to scale our infrastructure, increasing the number of [title boundaries](https://www.planning.data.gov.uk/dataset/title-boundary) available on the platform. 
- We are improving [our service for data providers](https://provide.planning.data.gov.uk). The service is now more responsive, with faster loading times, clearer guidance and new features such as showing non-authoritative data from alternative public sources. All of these help LPAs understand, improve and maintain the quality of the data they’ve provided.
- We are bringing data quality checks directly into the service. This allows LPAs to validate data earlier, submit smaller datasets more easily, and publish high-quality data sooner - increasing the amount of trusted, authoritative data available on the platform.
- We are testing Extract with real planning documents and staff working at local planning authorities to understand where it helps most and where it needs improvement (also known as the [alpha phase](https://www.gov.uk/service-manual/agile-delivery/how-the-alpha-phase-works)). 
- We are improving the experience so it’s clearer, easier and faster to turn documents into trustworthy data, and ensuring that it outputs high-quality data reliably.

### Next

- We will increase the number of datasets available through the Provide service, including developer contributions and local plans.
- We will create an internal tool to get new data onto the platform faster, reducing the time between data being provided to us and users being able to access it.
- We will continue to scale our platform’s ability to transform large datasets, including index polygons and UPRNs.
- We will revisit how we play back data quality checks to LPAs, focusing on which tasks will have the greatest impact on their quality score.
- Invite 30-50 local planning authorities to use Extract during the [beta phase](https://www.gov.uk/service-manual/agile-delivery/how-the-beta-phase-works), ensuring that it works reliably and can be scaled to meet the demands of all local planning authorities in England.
- We will conduct an accessibility audit and ensure Extract is accessible to Web Content Accessibility Guidelines 2.2.
- We will continue to iterate and improve Extract based on feedback from local planning authorities using it day-to-day.

### Later

- We will explore alternative options for warehousing reporting data to make it cheaper to run the platform.
- We will implement more complex data quality checks so that the data is easier to trust.
- Make Extract available for all local planning authorities in England.

## Consuming data

We are making planning and housing data easier to access, understand and reuse - whether developers building planning tools, analysts working with large datasets, or policymakers needing reliable evidence.

### Now

- We are publishing live platform performance metrics, so users can clearly understand reliability and availability.
- We are publishing dataset quality and coverage information, so users can understand what data we currently have.
- We are improving map search by Local Planning Authority and Town, so users can find relevant data more easily.

### Next

- We plan to provide datasets in formats such as Parquet to support large‑scale analysis and reuse.
- We intend to package datasets around common user needs, with clearer context and guidance, to make them easier to use and consume.

### Later

- We expect to improve discoverability on the search and map through smarter, more intuitive search.
- We will explore whether lightweight authenticated access, such as API keys, could support enhanced services while maintaining open access to data.
