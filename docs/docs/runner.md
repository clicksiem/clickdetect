# Runner

The runner is configured via a YAML file (default: `runner.yml`). It defines the datasource, webhooks, and detectors for the application.

## Structure

```yaml
datasource:
    type: <datasource_type>
    # ... datasource-specific fields

webhooks:
    <webhook_name>:
        type: <webhook_type>
        # ... webhook-specific fields

detectors:
    <detector_key>:
        name: "Display Name"
        for: "5m"
        description: "..."
        tenant: "default"
        active: true
        rules:
            - "path/to/rules/*.yml"
        webhooks:
            - <webhook_name>
        data:
            custom_key: value
```

## `datasource`

Only one datasource is configured per runner. See the [Datasources](datasource/index.md) section for available types and their configuration.

## `plugins`

An optional map of plugin configurations. The key is the plugin `id` and the value is the plugin-specific configuration object. See the [Plugins](plugin/index.md) section for available plugins and their options.

```yaml
plugins:
    <plugin_id>:
        option1: value1
```

## `webhooks`

A map of named webhook configurations. Each webhook has a `type` and type-specific fields. See the [Webhooks](webhooks/index.md) section for available types.

## `detectors`

A map of detector configurations. Each key is an internal identifier for the detector.

### Detector fields

| Field | Required | Default | Description |
|---|---|---|---|
| `name` | yes | — | Human-readable detector name |
| `for` | yes | — | Evaluation interval (e.g. `5m`, `1h`, `2d`) |
| `description` | no | `""` | Detector description |
| `tenant` | no | `"default"` | Tenant identifier, available in rule templates as `{{ detector.tenant }}` |
| `active` | no | `true` | Enable or disable the detector |
| `rules` | yes | — | List of rule file paths or glob patterns |
| `webhooks` | no | `[]` | List of webhook names to notify |
| `data` | no | `{}` | Custom key/value data passed to rule templates as `{{ detector.data }}` |

### Interval format

The `for` field accepts the following units:

| Unit | Suffix |
|---|---|
| Seconds | `s` |
| Minutes | `m` |
| Hours | `h` |
| Days | `d` |
| Weeks | `w` |
| Months | `mo` |
| Years | `y` |

Examples: `30s`, `5m`, `1h`, `7d`.

## Full example

```yaml
datasource:
    type: clickhouse
    host: 10.0.0.1
    port: 8123
    username: default
    password: secret
    database: soc
    verify: false

webhooks:
    http_sink:
        type: generic
        url: http://localhost:3000/alerts/create
        headers:
            X-Source: clickdetect

    teams_channel:
        type: teams
        url: https://outlook.office.com/webhook/...
        timeout: 10

detectors:
    fast_checks:
        name: "High-frequency checks"
        for: "5m"
        description: "Rules evaluated every 5 minutes"
        tenant: "acme"
        rules:
            - "rules/auth/*.yml"
            - "rules/network/*.yml"
        webhooks:
            - http_sink
            - teams_channel
        data:
            environment: production
```
