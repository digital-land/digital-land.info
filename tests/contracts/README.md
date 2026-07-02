# API Contract Tests

These files define the expected response shape for the entity JSON and GeoJSON API routes. They are written in [JSON Schema (Draft 2020-12)](https://json-schema.org/draft/2020-12), the same schema language used by OpenAPI internally. The `.schema.json` extension is the conventional suffix for JSON Schema files.

## Why contract tests?

The entity routes return dynamically constructed responses — the entity's `json` database column adds arbitrary additional fields, and the response is built manually rather than through FastAPI's `response_model`. This means type changes (e.g. a field changing from `integer` to `string`) are not caught by existing tests. Contract tests validate the shape and types of real API responses, giving consumers confidence that the structure is stable.

## Contracts

| File | Route |
|---|---|
| `entity_json.schema.json` | `GET /entity/{entity}.json` |
| `entity_search_json.schema.json` | `GET /entity.json` |
| `entity_geojson.schema.json` | `GET /entity/{entity}.geojson` |
| `entity_search_geojson.schema.json` | `GET /entity.geojson` |

## Key design decisions

- **Known fields** are listed explicitly in `properties` with their exact types.
- **Dynamic fields** (from the entity `json` column) are covered by `additionalProperties: { "type": "string" }`. These fields vary per entity but are always strings in the response.
- **`organisation-entity`** is typed as `["integer", "string"]` because it is an integer when set, but serialised as `""` (empty string) when null — a consequence of `NoneToEmptyStringEncoder` in the application.
- **GeoJSON geometry** coordinates are typed as `array` without constraining depth, since the structure varies by geometry type (Point, MultiPolygon, etc.).

## Updating contracts

If the API shape changes intentionally, update the relevant schema file to match and document why in the pull request. Unintentional changes should be investigated before updating.
