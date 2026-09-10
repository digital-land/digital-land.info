This roadmap shows our current plans for making it easier to find, use and trust planning and housing data.

We work in 3-month cycles and we aim to update this roadmap every 3 months. Our plans can change based on what we learn from speaking to our users, testing iterations, and how we can better deliver on our mission.

Last updated September 2026. Next update due January 20276.

## Designing data

We are designing and collecting data that is valuable to housing and planning, and improving the quantity of [data on the platform](https://www.planning.data.gov.uk/dataset/).

We regularly ask our community to help us decide the things we need to work on and tell us what they need from the data. See [how you can contribute](https://design.planning.data.gov.uk/how-to-contribute) and [get an existing dataset onto planning.data.gov.uk](https://design.planning.data.gov.uk/how-to-get-existing-datasets-on-to-planning-data-gov-uk).

### Now

- We are also working with an [advisory group](https://design.planning.data.gov.uk/advisory-group) to develop a set of open, reusable data specifications to underpin planning applications.
- We are continuing to add [local plan boundaries, documents and timetables](https://www.planning.data.gov.uk/entity/?dataset=local-plan-boundary&dataset=local-plan-document&dataset=local-plan-timetable&entry_date_day=&entry_date_month=&entry_date_year=) to the platform.
- We are making it easier for data consumers and planning policymakers to get involved in our [data design process](https://design.planning.data.gov.uk/data-design-process). We are also taking more data specifications related to local planning through the [Screen and Research stages](https://design.planning.data.gov.uk/planning-consideration/?stage=Screen&stage=Research&stage=%5B%27screen%27%5D) of our process.
- Based on our [data quality framework](https://digital-land.github.io/technical-documentation/data-operations-manual/Explanation/Key-Concepts/Data-quality-2-framework/), we’re introducing checks and changes to data management processes that will ensure the accuracy, consistency, and integrity of all datasets.

### Next

- We will be adding more datasets needed by the Planning Inspectorate and nationally significant infrastructure projects (consultees and geographies).
- We will draft a template Statutory Instrument for potential data standards.
- We will make it possible for local planning authorities to provide planning applications and decisions through our service.

### Later

- We will support the rollout of planning application submission and decision specifications.
- We will be adding further datasets as required to support emerging and existing planning legislation and guidance.

## Collecting and managing data

We are supporting local planning authorities across England to help them provide planning and housing data through our platform. Through the [Open Digital Planning community](https://opendigitalplanning.org/community-members), we’re supporting over 200 Local Planning Authorities (LPAs) to publish data, improve its quality and adopt digital planning products such as [PlanX](https://opendigitalplanning.org/services) and [BoPS](https://bops.digital). 

Alongside this, we are ensuring that our data collection pipeline remains performant as we grow the amount of data that we collect, standardise and index each night.

### Now

- We are making it faster and more reliable to build and rebuild planning data. Our platform can now be refreshed in hours rather than days, giving users quicker access to up-to-date, authoritative information. This work has also allowed us to scale our infrastructure to handle datasets containing millions of records, such as [title boundaries](https://www.planning.data.gov.uk/dataset/title-boundary).
- We are improving [our service for data providers](https://provide.planning.data.gov.uk) by speaking with users to understand their needs and prioritise future improvements.
- We are increasing the number of automated data quality checks we perform. Where we identify data quality concerns manually, we are turning these into repeatable checks that help us monitor and improve quality over time.
- We are developing an internal service to manage common data management tasks, including adding new data sources, configuring datasets and validating changes made by data providers.

### Next

- We will increase the number of datasets available through the Check & Provide service and redesign the service so it remains easy to use as the number of datasets grows.
- We will introduce authentication for actions that change data in the Check & Provide service, giving data providers secure access to more ways to manage their data.
- We will use our new processes for transforming large datasets to update Flood Risk Zone and Agricultural Land Classification data to new probability models, and identify other datasets that could benefit from the same approach.
- We will test how we present data quality scores to LPAs, focusing on the checks that have the greatest impact on quality and ensuring our approach works across the different dimensions of data quality before releasing it more widely.

### Later

- We will explore alternative ways of storing reporting data to reduce to cost of running the platform.
- We will make data quality scores available to data providers, helping them understand where their data can be improve and making authoritative planning data easier to trust.
- We will give data providers more ways to securely manage their own data and notify them when its quality changes.

## Consuming data

We are making planning and housing data easier to access, understand and reuse - whether developers building planning tools, analysts working with large datasets, or policymakers needing reliable evidence.

### Now

- We are publishing live platform performance metrics, so users can clearly understand reliability and availability.
- We are publishing dataset quality and coverage information, so users can understand what data we currently have.
- We are improving map search by Town, so users can find relevant data more easily.

### Next

- We intend to package datasets around common user needs, with clearer context and guidance, to make them easier to use and consume.

### Later

- We expect to improve discoverability on the search and map through smarter, more intuitive search.
- We will explore whether lightweight authenticated access, such as API keys, could support enhanced services while maintaining open access to data.
