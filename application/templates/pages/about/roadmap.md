This roadmap shows our current plans for making it easier to find, use and trust planning and housing data.

We work in 3-month cycles and we aim to update this roadmap every 3 months. Our plans can change based on what we learn from speaking to our users, testing iterations, and how we can better deliver on our mission.

Last updated October 2026. Next update due January 2027.

## Designing data

We are designing and collecting data that is valuable to housing and planning, and improving the quantity of [data on the platform](https://www.planning.data.gov.uk/dataset/).

We regularly ask our community to help us decide the things we need to work on and tell us what they need from the data. See [how you can contribute](https://design.planning.data.gov.uk/how-to-contribute) and [get an existing dataset onto planning.data.gov.uk](https://design.planning.data.gov.uk/how-to-get-existing-datasets-on-to-planning-data-gov-uk).

### Now

- We are working with the Spatial Development Strategy policy team to create standards for strategy timetables.
- We are carrying out user research to gather feedback at least once a month from a range of users and we will use what we learn to set priorities.
- We are agreeing shared data standards with HM Land Registry's Local Land Charges team.
- We are planning which datasets to collect next from local planning authorities.
- We are continuing our work on [planning permission submissions and decisions](https://design.planning.data.gov.uk/project/planning-applications).
- We are defining 4 new datasets from our planning considerations backlog and adding them to the platform.

## Collecting and managing data

We are supporting local planning authorities across England to help them provide planning and housing data through our platform. Through the [Open Digital Planning community](https://opendigitalplanning.org/community-members), we're supporting over 200 local planning authorities (LPAs) to publish data, improve its quality and adopt digital planning products such as [PlanX](https://opendigitalplanning.org/services) and [BoPS](https://bops.digital).

Alongside this, we are ensuring that our data collection pipeline remains performant as we grow the amount of data that we collect, standardise and index each night.

We publish more detailed roadmaps for the services behind this work: the [service local planning authorities use to check and provide data](https://provide.planning.data.gov.uk/roadmap), and the [internal service our team uses to manage it](https://manage.planning.data.gov.uk/roadmap). Both show what we have already delivered and the dates we are working towards.

### Now

- We are making it faster and more reliable to build and rebuild planning data. Our platform can now be refreshed in hours rather than days, giving users quicker access to up-to-date, authoritative information. This work has also allowed us to scale our infrastructure to handle datasets containing millions of records, such as [title boundaries](https://www.planning.data.gov.uk/dataset/title-boundary).
- We are increasing the number of automated data quality checks we perform. Where we identify data quality concerns manually, we are turning these into repeatable checks that help us monitor and improve quality over time.
- We are developing an internal service to manage common data management tasks, including adding new data sources, configuring datasets and validating changes made by data providers.

### Next

- We will increase the number of datasets available through the Check and provide your planning data service and redesign the service so it remains easy to use as the number of datasets grows.
- We will introduce authentication for actions that change data in the Check and provide your planning data service, giving data providers secure access to more ways to manage their data.
- We will use our new processes for transforming large datasets to update Flood Risk Zone and Agricultural Land Classification data to new probability models, and identify other datasets that could benefit from the same approach.

### Later

- We will explore alternative ways of storing reporting data to reduce the cost of running the platform.
- We will test how we present data quality scores to LPAs, focusing on the checks that have the greatest impact on quality and ensuring our approach works across the different dimensions of data quality before releasing it more widely.
- We will make data quality scores available to data providers, helping them understand where their data can be improved and making authoritative planning data easier to trust.
- We will give data providers more ways to securely manage their own data and notify them when its quality changes.

## Consuming data

We are making land and housing data easier to find, understand, use and trust.

### Now

- We are improving our search, so that it is easier and faster for users to find relevant data.
- We are making the map easier to use, including improving the way we list results and show where the map has no data.
- We are allowing users to download full search results, pages and datasets from the map.
- We are showing our data quality and coverage on dataset pages.
- We are improving the way that we tell users about new data and features.
- We are publishing a performance page using data from Google Analytics and our API.

### Next

- We will allow users to draw an area on the map and search within it.
- We will let users search the map by location.
- We will make data consistent across the map and dataset pages.
- We will create data packages for planning application submissions and brownfield land.
- We will publish our datasets on [data.gov.uk](https://data.gov.uk/).

### Later

- We plan to explore whether some features should need users to sign in.
- We plan to explore a Model Context Protocol (MCP) server, so that AI tools can use our data.
