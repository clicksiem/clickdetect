Made in :brazil:

---

# Clickdetect

![clickdetect running](docs/docs/assets/clickdetect-runner-demo.avif)

Clickdetect is a generic alerting and detection engine that supports any data source and integrates with any webhook. It is vendor-agnostic, with no lock-in, and enables powerful, flexible detection workflows.

Follow the doc: [https://clickdetect.souzo.me](https://clickdetect.souzo.me)

## Core Concepts

- Runner.yml: The file where you configure everything
- Detector: Component that runs rules based on thresholds
- Rule: File with structured format to define datasource analysis
- Datasource: Where rule queries are executed, like a database or another SIEM engine
- Webhooks: Where alerts are sent
- Plugin: Script that can intercept Clickdetect actions like "on_rule_triggered"

## Supported Integrations

### Datasources

- Clickhouse 
- Loki
- VictoriaLogs
- PostgreSQL
- Elastic
- Opensearch

### Webhooks

- Generic
- DFIR Iris
- Forgejo
- Email
- Microsoft Teams
- Slack
- Telegram
- Discord

### Plugins

- clickagentic: LLM AI Agent that analyzes your alerts

## Quick Start

Start by creating a `runner.yml` file — see the full reference in the [documentation](https://clickdetect.souzo.me).

### uv

Follow uv installation in [https://docs.astral.sh/uv](https://docs.astral.sh/uv)

```sh
uv sync --no-dev
uv run clickdetect --api
```

### Docker/Podman

#### Local

```sh
podman build -t clickdetect .
podman run -v ./runner.yml:/app/runner.yml -p 8080 clickdetect --api -p 8080
```

#### GitHub Packages

```sh
podman run -v ./runner.yml:/app/runner.yml -p 8080 ghcr.io/clicksiem/clickdetect:latest --api -p 8080
```

## Options

| Flag | Default | Description |
|---|---|---|
| `--api` | off | Start the REST API server |
| `-p`, `--port` | `8080` | Port for the API server |
| `-r`, `--runner` | `runner.yml` | Path to the runner configuration file |
| `--stdin` | off | Read the runner configuration from stdin |
| `--verbose` | off | Verbose mode |
| `--reload` | off | Hot reload rules |
| `--no-start` | off | Do not start detectors on start |
| `--list-webhooks` | off | List webhooks |
| `--list-datasources` | off | List datasources |
| `--list-plugins` | off | List all plugins |

## Runner Configuration

```yaml
datasource:
    type: clickhouse
    host: localhost
    port: 8123
    verify: false
    username: default
    password: default
    database: siem

webhooks:
    generic_webhook:
        type: generic
        url: <webhook_url>
        headers:
          X-Type: test

detectors:
    5m_detector:
        name: "5m interval"
        for: "5m"
        tenant: 'all' 
        description: "detect rules with 5 min interval"
        rules:
            - "<your rule path>"
        webhooks:
            - generic_webhook
        data:
          var1: '<var>' # variables to send
plugins:
  clickagentic: # plugin id
    provider: 'openai' # provider: openai, anthropic, google, huggingface, ollama, openrouter, deepseek
    model: 'gpt-5.2' # get model from your provider
    token: 'xxx'
    from_level: 10 # only run for alerts with alert level >= 10
    ids:
      - "id1"
```

More example of runner in [example_rules](./example_rules/)

## Rule Configuration

```yaml
id: "00000000-0000-0000-0000-000000000000"
name: "Base rule for help"
level: 1
size: ">0"
active: false
author: 
    - Vinicius Morais <me@souzo.me>
group: < group >
tags: 
    - <tags>
data: # variables sent to rules by jinja
    max_match_time: 5
rule: |-
    < rule >
```

## Release

See the latest [releases and changelog](https://github.com/clicksiem/clickdetect/releases)

## Contact

* E-mail: me@souzo.me
* Matrix: @souzo:matrix.org
* Linkedin: [https://www.linkedin.com/in/vinicius-m-a76ba51b5/](https://www.linkedin.com/in/vinicius-m-a76ba51b5/)
