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
        headers: # optional default({})
            X-Custom-Header: value
        verify: false # optional default(false)
```

## Priority mapping

The alert priority is derived from the rule `level` field:

| Rule level | OpsGenie priority |
|---|---|
| 0 – 3 | P5 — Lowest |
| 4 – 7 | P4 — Low |
| 8 – 10 | P3 — Moderate |
| 11 – 13 | P2 — High |
| 14 – 15 | P1 — Critical |

## Notes

- Authentication uses the `Authorization: GenieKey <api_key>` header.
- `alias` is set to the rule ID, so repeated firings of the same rule are deduplicated into the same OpsGenie alert until it's closed.
- `tags` is populated from `rule.tags`.
- `details` includes the rule ID, detector name and tenant.
- A successful request returns `202 Accepted` (OpsGenie processes alerts asynchronously).
- Header keys are normalized to lowercase.
