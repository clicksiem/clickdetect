# TheHive Hook

Send alerts to [TheHive](https://strangebee.com/thehive/) via the `/api/v1/alert` API endpoint.

## Config

```yaml
webhooks:
    thehive_hook:
        type: thehive # required
        url: https://thehive.example.com # required
        api_key: '...' # required
        type: clickdetect # optional default(clickdetect), alert type
        source: clickdetect # optional default(clickdetect), alert source
        tlp: 2 # optional default(2), Traffic Light Protocol level (0=WHITE, 1=GREEN, 2=AMBER, 3=RED)
        pap: 2 # optional default(2), Permissible Actions Protocol level (0=WHITE, 1=GREEN, 2=AMBER, 3=RED)
        severity_map: # optional, minimum rule level of each severity band
            critical: 90
        headers: # optional default({})
            X-Custom-Header: value
        verify: false # optional default(false)
```

## Severity mapping

The rule `level` is resolved into a [severity band](../rules.md#severity-levels), which maps
to TheHive as:

| Band | TheHive severity |
|---|---|
| `informational` | 1 — Low |
| `low` | 1 — Low |
| `medium` | 2 — Medium |
| `high` | 3 — High |
| `critical` | 4 — Critical |

TheHive has no informational severity, so that band falls back to Low. Use the
`severity_map` option to change the rule level at which each band starts.

## Notes

- `sourceRef` is a randomly generated UUID per alert, since TheHive requires a unique reference per `source`.
- `tags` is populated from `rule.tags`.
- `summary` contains the raw query result data, serialized as JSON.
- Header keys are normalized to lowercase.
