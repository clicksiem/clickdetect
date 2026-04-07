# Opensearch

Query events from an Opensearch index.

## Config

```yaml
datasource:
    type: opensearch    # required
    url: localhost      # required
    index: my-index-*   # required
    username: open      # optional
    password: pass      # optional
    verify: false       # optional default(false) — use https when true
```

## Notes

- Authentication: use either basic `username`/`password`.
- The `rule` query must be a valid Opensearch Query DSL JSON string (e.g. `{"query": {"match_all": {}}}`).
- The result count (`data.len`) is the number of hits returned.
- Each result row contains `_id`, `_index`, and all fields from `_source`.
