# Elasticsearch

> Elasticsearch integration is under testing - Can you help me? open an issue!


Query events from an Elasticsearch index.

## Config

```yaml
datasource:
    type: elasticsearch # required
    host: localhost     # required
    port: 9200          # required
    index: my-index-*   # required
    username: elastic   # optional
    password: pass      # optional
    api_key: '...'      # optional — takes precedence over username/password
    verify: false       # optional default(false) — use https when true
```

## Notes

- Authentication: use either `username`/`password` or `api_key`.
- The `rule` query must be a valid Elasticsearch Query DSL JSON string (e.g. `{"query": {"match_all": {}}}`).
- The result count (`data.len`) is the number of hits returned.
- Each result row contains `_id`, `_index`, and all fields from `_source`.
