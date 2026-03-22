# Loki

Query log streams from Grafana Loki.

## Config

```yaml
datasource:
    type: loki       # required
    host: localhost  # required
    port: 3100       # optional
    username: admin  # optional
    password: pass   # optional
    verify: false    # optional default(false) — use https when true
    org_id: '...'    # optional — sets X-Scope-OrgID header (multi-tenant)
```

## Notes

- The `rule` query must be a valid LogQL expression (e.g. `{job="app"} |= "error"`).
- Results are fetched via `query_range` with a limit of 5000 log lines.
- The result count (`data.len`) is the total number of log lines returned.
- Each result row contains `timestamp`, `line`, and all stream labels.
