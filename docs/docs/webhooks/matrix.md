# Matrix Hook

> Is under development

Send alert to matrix

## Config 

```yaml
webhooks:
    matrix_hook:
        type: matrix # required
        url: https://matrix.org # required
        username: '...' # required
        password: '...' # required
        room_id: '...' # required
        verify: true # optional default(true)
        template: '{{ rule.name }}' # optional default(DEFAULT_TEMPLATE)
```
