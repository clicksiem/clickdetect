# AlertManager Hook

Send alerts to [Prometheus AlertManager](https://prometheus.io/docs/alerting/latest/alertmanager/) via the `/api/v2/alerts` endpoint.

## Config

```yaml
webhooks:
    alertmanager_hook:
        type: alertmanager # required
        url: http://alertmanager:9093 # required, base URL (without /api/v2/alerts)
        labels: # optional default({}), merged into the alert labels
            environment: production
        generator_url: https://clicksiem.example.com # optional default('')
        expire_after: 3600 # optional default(0), seconds until the alert auto resolves
        severity_map: # optional, minimum rule level of each severity band
            critical: 90
        headers: # optional default({})
            X-Custom-Header: value
        verify: false # optional default(false)
```

## Severity mapping

The rule `level` is resolved into a [severity band](../rules.md#severity-levels), which
becomes the `severity` label:

| Band | `severity` label |
|---|---|
| `informational` | `info` |
| `low` | `low` |
| `medium` | `medium` |
| `high` | `high` |
| `critical` | `critical` |

Use the `severity_map` option to change the rule level at which each band starts.

## Labels

| Label | Value |
|---|---|
| `alertname` | Rule name |
| `severity` | Mapped from the rule level |
| `level` | Rule level |
| `rule_id` | Rule ID |
| `group` | Rule group |
| `detector` | Detector name |
| `tenant` | Detector tenant |
| `source` | `clickdetect` |

Labels from the `labels` option are merged last and override the ones above.

## Annotations

`summary` (rule name), `description` (rule description, falling back to the name), `tags` (comma separated `rule.tags`) and `results` (the JSON encoded query result).

## Notes

- AlertManager has no built-in authentication; use the `headers` option to pass an `Authorization` header when it sits behind a proxy.
- Label values are always sent as strings and empty ones are dropped, as required by AlertManager.
- `startsAt` is the detector query start time.
- With `expire_after` unset, the alert stays active until AlertManager's own `resolve_timeout` expires it.
- Header keys are normalized to lowercase.
