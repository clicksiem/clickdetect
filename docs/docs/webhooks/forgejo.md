# Forgejo hook

Send alert to smtp

## Config 

```yaml
webhooks:
    forgejo_hook:
        type: forgejo # required
        url: https://codeberg.org # required
        owner: '...' # required
        repository: '...' # required
        token: '...' # required
        title: 'alert: {{ rule.name }}' # optional default(alert: {{rule.name}})
        template: '...' # optional default(DEFAULT_TEMPLATE)
```

## Notes

- Title can use a jinja2 template.
- Header keys are normalized to lowercase.
