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
        headers: # optional default({})
            X-Custom-Header: value
        verify: false # optional default(false)
```

## Severity mapping

The alert severity is derived from the rule `level` field:

| Rule level | TheHive severity |
|---|---|
| 0 – 3 | 1 — Low |
| 4 – 7 | 2 — Medium |
| 8 – 10 | 3 — High |
| 11 – 15 | 4 — Critical |

## Notes

- `sourceRef` is a randomly generated UUID per alert, since TheHive requires a unique reference per `source`.
- `tags` is populated from `rule.tags`.
- `summary` contains the raw query result data, serialized as JSON.
- Header keys are normalized to lowercase.
