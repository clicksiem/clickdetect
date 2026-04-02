# Loki

Query log streams from Grafana Loki.

## Config

```yaml
datasource:
    type: loki                          # required
    url: http://localhost:3100          # required
    username: admin                     # optional
    password: pass                      # optional
    verify: false                       # optional default(false) — verify SSL certificate
    org_id: '...'                       # optional default('fake') — sets X-Scope-OrgID header (multi-tenant)
```

## Notes

- The `rule` query must be a valid LogQL expression (e.g. `{job="app"} |= "error"`).
- Results are fetched via `query_range` with a limit of 5000 log lines.
- The result count (`data.len`) is the total number of log lines returned.
- Each result row contains `timestamp`, `line`, and all stream labels.
