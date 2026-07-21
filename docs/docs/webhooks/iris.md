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
        severity_map: # optional, minimum rule level of each severity band
            critical: 90
        headers: # optional default({})
            X-Custom-Header: value
        verify: false # optional default(false)
```

## Severity mapping

The rule `level` is resolved into a [severity band](../rules.md#severity-levels), which maps
to DFIR-IRIS as:

| Band | DFIR-IRIS severity |
|---|---|
| `informational` | 1 — Informational |
| `low` | 2 — Low |
| `medium` | 3 — Medium |
| `high` | 4 — High |
| `critical` | 5 — Critical |

Use the `severity_map` option to change the rule level at which each band starts.

## Notes

- `alert_tags` is populated from `rule.tags`, joined by `, `.
- `alert_source_content` contains the raw query result data in JSON.
- `alert_status_id` is always `2` (New) on creation.
- Header keys are normalized to lowercase.
