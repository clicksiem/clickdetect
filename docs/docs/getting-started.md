# Getting Started

## Using uv

Follow uv installation [https://docs.astral.sh/uv/](https://docs.astral.sh/uv/)

Clone, sync and run!

```sh
git clone https://github.com/clicksiem/clickdetect
uv sync 
uv run clickdetect --api --reload
```

## Using Docker/Podman

### 1. Pull image

```sh
podman pull ghcr.io/clicksiem/clickdetect:latest
```

### 2. Create compose.yml

```yaml
services:
    clickdetect:
        image: ghcr.io/clicksiem/clickdetect:latest
        ports:
            - 8080:8080
        command: --api
        volumes:
            - ./runner.yml:/app/runner.yml
```

### 3. Configure runner

Create a `runner.yml` file at the project root:

```yaml
datasource:
    type: clickhouse
    host: localhost
    port: 8123
    username: default
    password: pass
    database: default

webhooks:
    my_webhook:
        type: generic
        url: http://localhost:3000/alerts

detectors:
    5m_detector: # detector that runs every 5 minutes
        name: "5 minute checks"
        for: "5m" 
        description: "Detect rules every 5 minutes"
        tenant: "default" 
        rules: # if you not specify the directory, It will be the current directory of project. (in docker is /app)
            - "5m_rule.yml" 
            - "rules/*.yml"
        webhooks:
            - my_webhook

    1m_detector: # detector that runs every 1 minutes
        name: "1 minute checks"
        for: "1m" 
        description: "Detect rules every 1 minutes"
        tenant: "default" 
        rules:
            - "1m_rule.yml" 
        webhooks:
            - my_webhook
```

See the [Runner](runner.md) page for the full configuration reference.

### 4. Write a rule

Create a rule file (e.g. `rules/brute_force.yml`):

```yaml
id: "001"
name: Brute Force Detected
level: 8
size: ">5" # condition to trigger the rule ( >=, >, <. <=, == )
active: true
author:
    - Your Name <you@example.com>
group: authentication
tags:
    - authentication_failed
    - bruteforce
description: "More than 5 failed login attempts in the last minute"
rule: |-
    SELECT count(*) AS cnt
    FROM auth_logs
    WHERE
        timestamp >= now() - INTERVAL 1 MINUTE
        AND status = 'failed'
        AND tenant = '{{ detector.tenant }}'
```

See the [Rules](rules.md) page for all rule fields and the available Jinja2 template variables.

### 5. Run and have fun

```sh
podman compose up -d
```

Fastest way

```sh
podman run ghcr.io/clicksiem/clickdetect:latest
```
