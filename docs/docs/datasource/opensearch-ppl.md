# Opensearch PPL

Query events from an Opensearch index using the [Piped Processing Language (PPL)](https://opensearch.org/docs/latest/search-plugins/sql/ppl/index/).

## Config

```yaml
datasource:
    type: opensearch-ppl  # required
    url: http://localhost:9200  # required
    username: admin           # optional
    password: pass            # optional
    verify: false             # optional default(false) — use https when true
```

## Notes

- Unlike the `opensearch` datasource (which uses Query DSL), this datasource sends PPL queries to the `/_plugins/_ppl` endpoint.
- The `rule` query must be a valid PPL statement (e.g. `source=my-index | where status='failed'`).
- The result count (`data.len`) is the value of the `size` field returned by the API.
- Sigma rules are supported via the `opensearch-ppl` backend.
