# Dev entity search comparison

Both routes and correlated stage logs are active without configuration flags.
The comparison route is available wherever this code is deployed.
No database migration is needed.

Use identical query parameters on:

- `/entity.json`: current optimised search.
- `/entity2.json`: original search from `main` commit `3bf1be43`.

For example:

```text
/entity2.json?geometry_curie=statistical-geography:E12000007&geometry_curie=statistical-geography:E09000007&geometry_relation=within&period=current&limit=10&dataset=listed-building
```

Run one request at a time, alternating routes. Compare counts and entities;
pagination links necessarily use different route paths. The baseline deliberately
retains main's grouping behaviour: if the dev relation lacks a recognised primary
key, it may reproduce the grouping error. That is diagnostic evidence, not a
successful timing comparison.

## Finding the time spent

Sentry spans use `op=entity.search` and follow the existing trace sampling policy.
Stage-start and stage-end INFO logs are sent to Sentry Logs (when configured)
and application logs independently of trace sampling. No sampling change is
required to get the stage timing logs. Filter by
`search_variant` (`main` or `optimized`) and correlate with `search_request_id`.
`search_parameters_hash` matches equivalent sorted raw query parameter pairs
across the two routes; it does not contain raw parameter values.

Stages:

- `request.total`: time in the shared route handler, including nested stages.
- `db.acquire_connection`: connection acquisition, including pool wait,
  connection creation and pre-ping if required.
- `metadata.datasets`, `metadata.typologies`: metadata/cache lookups.
- `area.lookup`: optional external postcode/UPRN lookup.
- `filters.validate`: filter validation.
- `query.build`, `count_query.build`, `page_query.build`, `shared_query.build`:
  SQLAlchemy query construction.
- `count.execute_fetch` and `page.execute_fetch`: baseline count/page calls.
- `shared_query.execute_fetch`: optimised single-statement call.
- `models.convert`: building entity response models.
- `response.format`: JSON/GeoJSON model formatting or HTML rendering and facets.

Execution/fetch spans include SQL execution, transfer and SQLAlchemy row
processing; they are not server-only query timings. `request.total` excludes
FastAPI dependency setup/teardown and final framework response encoding/send;
use the parent HTTP transaction for the broader application request duration.
Nested span durations must not be added together.

A start without an end identifies an unfinished stage. A gateway 504 does not
necessarily stop the application query; check later logs for completion/error
before repeating a request. No extra EXPLAIN or benchmark queries are executed.
The existing `entity.search.duration` metric now also carries `search.variant`;
compare the same `search.group` and release for each variant.

Remove the temporary comparison route and verbose diagnostics when the investigation is complete.

## Comparing results

The `response.measure` and `request.total` end logs/spans include:

- `total_matches`: database count before pagination.
- `returned_rows`: number of entities in the returned page.
- `response_body_bytes`: uncompressed UTF-8 response body size, including links.
- `results_bytes`: canonical JSON byte size of the entities/features only.
- `results_sha256`: hash of those records, including values and array order.

Compare counts and `results_sha256` for identical requests against the same data.
The hash ignores object-key order and pagination links, since the two endpoint
paths differ. Size/count equality alone does not prove records match. JSON and
GeoJSON include the results hash; HTML has counts and rendered body size only.
No entity contents are logged. `response.measure` includes an additional JSON
encoding pass and hashing; it is diagnostic overhead included in `request.total`.
The body size is before any proxy compression and excludes HTTP headers.
