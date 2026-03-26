# Clickdetect

Clickdetect is a SIEM engine on steroids, no lock-in with any vendors and powerfull detection.

Follow the doc: [https://clickdetect.souzo.me](https://clickdetect.souzo.me)

## Starting guide

First of all, create your runner.yml file. (Follow doc for the creation)
You will put detectors, webhooks and datasources in the configuration file.

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

#### Github Packages

```sh
podman run -v ./runner.yml:/app/runner.yml -p 8080 ghcr.io/clicksiem/clickdetect:latest --api -p 8080
```

## Roadmap

### Webhooks

- [ ] Complete DFIR-IRIS webhook integration
- [ ] Add Slack webhook
- [ ] Add Discord webhook
- [ ] Add PagerDuty webhook
- [ ] Add Telegram webhook
- [ ] Add Opsgenie webhook

### Alert Management

- [ ] Implement timeframe-based alert grouping (avoid duplicate alerts within a window)
- [ ] Implement alert silencing (suppress alerts by rule/group/tenant for a duration)
- [ ] Add API endpoints to manage silences (`POST /silence`, `DELETE /silence/{id}`)

### Rule Management

- [x] Hot reload rules without restarting (`--reload` flag or file watcher) ✅
- [ ] API endpoints to add/update/remove rules dynamically (depends on hot reload)
- [ ] Sigma rule conversion support (`sigma: true` in rule definition)

### Datasources

- [ ] Add support for Splunk
- [ ] Add support for OpenSearch
- [ ] Add support for Prometheus/VictoriaMetrics (metrics-based detection)

### API & Observability

- [ ] Implement an endpoint to create, edit and delete rules
- [ ] Alert history endpoint to query past triggered rules

## Contact-me

* E-mail: me@souzo.me
* Matrix: @souzo:matrix.org
* Linkedin: [https://www.linkedin.com/in/vinicius-m-a76ba51b5/](https://www.linkedin.com/in/vinicius-m-a76ba51b5/)
