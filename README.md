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

## Next steps

* Add minimal 10 webhooks []
* Implement timeframe []
    - Group Alerts
    - Silence alerts 
* Add silence alerts endpoint for api []
* Add sigma convertion in rules []
    - like: sigma: true
* Hot reload for rules []
    - add option like --reload
* Add api endpoint to add/remove/update new rules []
    - file hot reload will make this possible

## Contact-me

* E-mail: me@souzo.me
* Matrix: @souzo:matrix.org
* Linkedin: [https://www.linkedin.com/in/vinicius-f-a76ba51b5/](https://www.linkedin.com/in/vinicius-f-a76ba51b5/)
