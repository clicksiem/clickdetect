# Generic Hook

Send alert to any HTTP endpoint via POST request.

## Config

```yaml
webhooks:
    generic_hook:
        type: generic # required
        url: https://example.com/webhook # required
        headers: # optional default({})
            Authorization: 'Bearer token'
        verify: false # optional default(false)
        timeout: 10 # optional default(10)
        template: '{"rule": {{ rule | tojson }}, "data": {{ data | tojson }}, "detector": {{ detector | tojson }} }' # optional default(DEFAULT_TEMPLATE)
```

## Notes

- If no `content-type` header is provided, it defaults to `application/json`.
- Header keys are normalized to lowercase.
