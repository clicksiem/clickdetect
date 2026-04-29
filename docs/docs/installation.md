# Installation

## Requirements

- Python >= 3.13
- [uv](https://docs.astral.sh/uv/) package manager

# Run with uv

Clone repository

```sh
git clone https://github.com/clicksiem/clickdetect
```

## Install dependencies

```sh
uv sync --no-dev
```

### For development (includes mkdocs and other dev tools):

```sh
uv sync
```

## Run

```sh
uv run clickdetect [OPTIONS]
```

### Options

| Flag | Default | Description |
|---|---|---|
| `--api` | off | Start the REST API server |
| `-p`, `--port` | `8080` | Port for the API server |
| `-r`, `--runner` | `runner.yml` | Path to the runner configuration file |
| `--stdin` | off | Read the runner configuration from stdin |
| `--verbose` | off | Verbose mode |
| `--reload` | off | Hot reload rules |
| `--no-start` | off | Do not start detectors on start |
| `--list-webhooks` | off | List all available webhook types and exit |
| `--list-datasources` | off | List all available datasource types and exit |
| `--list-plugins` | off | List all plugins |


# Docker / Podman

## Local

### Build
```sh
podman build -t clickdetect .
```

### Run

```sh
podman run --rm -v ./runner.yml:/app/runner.yml -p 8080:8080 clickdetect --api
```

## Github Packages

#### Pull

```
podman pull ghcr.io/clicksiem/clickdetect:latest
```

#### Run
```sh
podman run -v ./runner.yml:/app/runner.yml -p 8080:8080 ghcr.io/clicksiem/clickdetect:latest --api -p 8080
```

## Docker/Podman compose

#### compose.yml

```yaml
services:
    clickdetect:
        image: ghcr.io/clicksiem/clickdetect:latest
        network_mode: host
        command: --api
        volumes:
            - ./runner.yml:/app/runner.yml
```

#### Run

```sh
podman compose up -d
```

