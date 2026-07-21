Made in :brazil: | ![GitHub Repo stars](https://img.shields.io/github/stars/clicksiem/clickdetect)

---

# Clickdetect

![clickdetect running](docs/docs/assets/clickdetect-runner-demo.avif)

ClickDetect is a vendor-agnostic alerting framework for threshold-based detection. 

It have a flexible integration system for datasource and webhooks to easly integrate your platform. 

Follow the documentation: [https://clickdetect.souzo.me](https://clickdetect.souzo.me)

## Core Concepts

This is the core concepts for clickdetect.

- Runner.yml: The file where you configure everything
- Detector: Component that runs rules based on thresholds
- Rule: File with structured format to define datasource analysis
- Datasource: Where rule queries are executed, like a database or another SIEM engine
- Webhooks: Where alerts are sent
- Plugin: Script that can intercept Clickdetect actions like `on_rule_triggered`

## Supported Integrations

These are the active integrations, but they are not limited to them.

### Datasources

- Clickhouse 
- Loki
- VictoriaLogs
- PostgreSQL
- Elastic
- Opensearch
- Opensearch PPL
- Databricks
- Duckdb

### Webhooks

- Generic
- DFIR Iris
- Forgejo
- Email
- Microsoft Teams
- Slack
- Telegram
- Discord
- TheHive
- Opsgenie
- AlertManager

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
podman run -v ./runner.yml:/app/runner.yml -p 8080:8080 clickdetect --api -p 8080
```

#### GitHub Packages

```sh
podman run -v ./runner.yml:/app/runner.yml -p 8080:8080 ghcr.io/clicksiem/clickdetect:latest --api -p 8080
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
| `--sigma` | off | Treat all rules as Sigma rule |
| `--version` | off | Print version and exit |

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
        sigma: true # threat all rules for this detector as sigma rule
        webhooks:
            - generic_webhook
        data:
          var1: '<var>' # variables to send
plugins:
  clickagentic: # plugin id
    provider: 'openai' # provider: openai, anthropic, google, huggingface, ollama, openrouter, deepseek
    model: 'gpt-5.2' # get model from your provider
    token: 'xxx'
    from_level: 60 # only run for alerts with alert level >= 60
    ids:
      - "id1"
```

More example of runner in [example_rules](./example_rules/)

## High Availability

By default Clickdetect runs as a single process and keeps the detection window of each detector in memory, so two instances sharing a config would emit duplicate alerts.

Adding a top-level `redis` block turns it into an active-passive, multi-replica setup with automatic failover:

```yaml
redis:
    url: redis://localhost:6379/0
    namespace: clickdetect # optional
    lock_ttl: 1500 # optional, failover latency in seconds
```

Every detector run takes a distributed lock, so only one replica evaluates a given window, and the window itself is stored in Redis, so a replica taking over resumes from exactly where the previous one stopped — no gaps, no reprocessing. Run identical replicas against the same `runner.yml` and the same Redis.

See [High Availability](https://clickdetect.souzo.me/high-availability/) for details.

## Rule Configuration

You can configure your rules using `yaml` format. The field `rule` is generic, you can put your DQL, SQL, LogQL or whatever you have configured on the datasource.


```yaml
id: "00000000-0000-0000-0000-000000000000" # id of your rule
name: "Base rule for help" # name of your rule
level: 50 # rule level
size: ">0" # >, <, =, >=, <= this define if the values returned by the query will trigger an alert
sigma: false # If the rule will be treated as Sigma Rule. this depends if your datasource supports sigma.
active: false # if the rule is active
author: # rule author
    - Vinicius Morais <me@souzo.me>
group: < group > # rule groups
tags:  # rule tags
    - <tags>
data: # variables sent to rules by jinja
    max_match_time: 5
rule: |- # your rule based on your datasourcec
    < rule >
```

## Severity

A rule's `level` is an integer from `0` to `100` — anything outside that range makes the rule fail to load. Sigma rules use a textual level (`informational`, `low`, `medium`, `high`, `critical`), which is converted to that scale on load.

Since every destination has its own severity vocabulary, the level is first resolved into a band:

| Band | Level |
|---|---|
| `informational` | 0 |
| `low` | 20 |
| `medium` | 40 |
| `high` | 60 |
| `critical` | 80 |

Each webhook then translates the band into what its destination expects. The bands are configurable per webhook with `severity_map`, which sets the minimum rule level of each band — bands left out keep their default:

```yaml
webhooks:
    opsgenie_hook:
        type: opsgenie
        api_key: 'xxx'
        severity_map:
            high: 70
            critical: 90
```

See [Severity levels](https://clickdetect.souzo.me/rules/#severity-levels) for details.

## Release

See the latest [releases and changelog](https://github.com/clicksiem/clickdetect/releases)

## Contact

You can find me using this methods.

* *E-mail*: me@souzo.me
* *Matrix*: @souzo:matrix.org
* *Linkedin*: [https://www.linkedin.com/in/vinicius-m-a76ba51b5/](https://www.linkedin.com/in/vinicius-m-a76ba51b5/)
* *Twitter/X*: [https://x.com/souzomain](https://x.com/souzomain)
* *Reddit*: [https://www.reddit.com/user/_souzo/](https://www.reddit.com/user/_souzo/)
