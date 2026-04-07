# DFIR-IRIS Hook

Send alerts to [DFIR-IRIS](https://dfir-iris.org) via the `/alerts/add` API endpoint.

## Config

```yaml
webhooks:
    iris_hook:
        type: iris # required
        url: https://iris.example.com # required
        api_key: '...' # required
        customer_id: 1 # required
        headers: # optional default({})
            X-Custom-Header: value
        verify: false # optional default(false)
```

## Severity mapping

The alert severity is derived from the rule `level` field:

| Rule level | DFIR-IRIS severity |
|---|---|
| 0 – 3 | 1 — Informational |
| 4 – 7 | 2 — Low |
| 8 – 10 | 3 — Medium |
| 11 – 13 | 4 — High |
| 14 – 15 | 5 — Critical |

## Notes

- `alert_tags` is populated from `rule.tags`, joined by `, `.
- `alert_source_content` contains the raw query result data in JSON.
- `alert_status_id` is always `2` (New) on creation.
- Header keys are normalized to lowercase.
