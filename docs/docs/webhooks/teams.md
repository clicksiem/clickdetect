# Teams Hook

Send alert to Microsoft Teams via incoming webhook.

## Config

```yaml
webhooks:
    teams_hook:
        type: teams # required
        url: https://outlook.office.com/webhook/... # required
        verify: false # optional default(false)
        timeout: 10 # optional default(10)
        template: '...' # optional default(DEFAULT_TEMPLATE)
```

## Default Template

```json
{
    "@type": "MessageCard",
    "@context": "http://schema.org/extensions",
    "summary": "{{ rule.name }}",
    "sections": [{
        "activityTitle": "**[Level {{ rule.level }}] {{ rule.name }}**",
        "activitySubtitle": "{{ rule.description }}",
        "facts": [
            { "name": "Rule ID", "value": "{{ rule.id }}" },
            { "name": "Group", "value": "{{ rule.group }}" },
            { "name": "Tags", "value": "{{ rule.tags | join(', ') }}" },
            { "name": "Matches", "value": "{{ data.len }}" },
            { "name": "Detector", "value": "{{ detector.name }}" },
            { "name": "Tenant", "value": "{{ detector.tenant }}" }
        ],
        "markdown": true
    }]
}
```
