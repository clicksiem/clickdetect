# Slack Hook

Send alerts to a Slack channel via [Incoming Webhooks](https://api.slack.com/messaging/webhooks).

## Config

```yaml
webhooks:
    slack_hook:
        type: slack # required
        url: https://hooks.slack.com/services/... # required
        verify: true # optional default(true)
        timeout: 10 # optional default(10)
        template: '...' # optional default(DEFAULT_TEMPLATE)
```

## Notes

- The rendered template is sent as the `text` field of the Slack payload.
- Slack *mrkdwn* formatting is supported (e.g. `*bold*`, `_italic_`).
- To get a webhook URL, create an [Incoming Webhook app](https://api.slack.com/messaging/webhooks) in your Slack workspace.
