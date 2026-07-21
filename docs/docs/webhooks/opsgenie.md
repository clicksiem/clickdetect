# OpsGenie Hook

Send alerts to [OpsGenie](https://www.atlassian.com/software/opsgenie) via the Alert API v2 endpoint.

## Config

```yaml
webhooks:
    opsgenie_hook:
        type: opsgenie # required
        api_key: '...' # required
        url: https://api.opsgenie.com/v2/alerts # optional default(https://api.opsgenie.com/v2/alerts), use https://api.eu.opsgenie.com/v2/alerts for the EU instance
        source: clickdetect # optional default(clickdetect)
        severity_map: # optional, minimum rule level of each severity band
            critical: 90
        headers: # optional default({})
            X-Custom-Header: value
        verify: false # optional default(false)
```

## Priority mapping

The rule `level` is resolved into a [severity band](../rules.md#severity-levels), which maps
to OpsGenie as:

| Band | OpsGenie priority |
|---|---|
| `informational` | P5 — Lowest |
| `low` | P4 — Low |
| `medium` | P3 — Moderate |
| `high` | P2 — High |
| `critical` | P1 — Critical |

Use the `severity_map` option to change the rule level at which each band starts.

## Notes

- Authentication uses the `Authorization: GenieKey <api_key>` header.
- `alias` is set to the rule ID, so repeated firings of the same rule are deduplicated into the same OpsGenie alert until it's closed.
- `tags` is populated from `rule.tags`.
- `details` includes the rule ID, detector name and tenant.
- A successful request returns `202 Accepted` (OpsGenie processes alerts asynchronously).
- Header keys are normalized to lowercase.
