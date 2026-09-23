# Comparing entity search performance

`get_entity_search` emits the Sentry distribution `entity.search.duration` in
milliseconds. It measures query construction, the full count, result fetching,
and entity conversion. It excludes router validation and HTTP serialization.
The SQL and response are unchanged by this instrumentation.

Attributes:

- `search.group`: SHA-256 of nonempty parameters and response extension. Dictionary
  keys and order-independent filter lists are canonicalised, so reordering CURIEs
  does not split a group. Pagination and other parameter differences remain distinct.
  Explicit defaults and omitted defaults can produce different groups; replay the
  same URL when comparing releases.
- `search.geometry_curie`: sorted boundary CURIEs, for finding this benchmark.
- `extension`: response format, or `html`.
- `outcome`: `success` or `error`. Errors retain their original exception.
- `sentry.release` and `sentry.environment`: attached by the SDK from the existing
  `RELEASE_TAG` and `ENVIRONMENT` configuration. Set distinct release tags for each
  deployment.

In Sentry Metrics, select `entity.search.duration`, filter to the development
environment and this search's `search.group`, then chart average/p50/p95 duration
split by `sentry.release`. Separate `outcome` values so failed executions do not
look like successful performance improvements. Repeat the same request several
times per release; one request is not sufficient for a useful p95 comparison.

Benchmark request (GET):

```text
https://www.development.planning.data.gov.uk/entity.json?geometry_curie=statistical-geography:E07000212&geometry_curie=statistical-geography:E07000217&geometry_curie=statistical-geography:E10000030&geometry_relation=within&period=current&limit=100
```

Deploy the instrumentation before recording the baseline, then retain it through
the optimisation deployment. Keep parameters and data comparable. `limit=100`
still runs the full count before retrieving the page.

The pinned Sentry Python SDK enables metrics by default. Metrics are independent
of the transaction trace sample rate; a configured Sentry DSN and server-side
metrics availability are still required. No historical timings are backfilled.

A duration is emitted when the search returns or raises. A gateway 504 does not
necessarily stop the application query: its metric may arrive later and exceed
the HTTP timeout. A worker killed before finishing cannot emit its final duration.
Record HTTP status/time separately and do not interpret missing metrics as fast
searches. This measurement is application search time, not isolated database time.
