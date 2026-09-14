# API

The REST API is enabled with the `--api` flag. It runs on port `8080` by default (override with `-p`).

```sh
uv run clickdetect --api -p 8080
```

## API only mode

When `--api` is passed and the runner file does not exist, clickdetect starts with no datasource, webhooks, detectors or plugins, and everything is configured through the API.

```sh
uv run clickdetect --api
```

Create the resources in this order:

1. [`POST /datasource`](#post-datasource)
2. [`POST /webhooks`](#post-webhooks) and [`POST /plugins`](#post-plugins)
3. [`POST /detector`](#post-detector)
4. [`POST /rules/{detector_id}`](#post-rulesdetector_id)

!!! warning
    Resources created through the API are kept in memory only, they are lost when clickdetect restarts.

The create routes also work when clickdetect was started with a runner file.

---

## Health

### `GET /health/ok`

Returns a simple liveness check.

**Response:**
```json
{ "ok": true }
```

---

## Configuration

The request bodies use the same fields as the matching block in the [runner](runner.md), sent as JSON.

### `POST /datasource`

Creates the datasource and connects to it. Only one datasource is allowed, it is shared by all detectors.

**Request:**
```json
{
  "type": "clickhouse",
  "host": "localhost",
  "port": 8123,
  "username": "default",
  "password": "default",
  "database": "soc"
}
```

**Response (`201`):** the datasource configuration, without sensitive fields.
```json
{ "type": "clickhouse", "database": "soc", "port": 8123, "verify": false }
```

---

### `POST /webhooks`

Creates a webhook. `name` is the identifier referenced by detectors in `webhooks`. If a detector already references the name, the webhook is attached to it.

The `template` is validated on creation, a template with syntax errors returns `422`.

**Request:**
```json
{
  "name": "generic_webhook",
  "type": "generic",
  "url": "http://localhost:3000/alerts/create/clickdetect",
  "headers": { "X-Type": "test" },
  "template": "{ \"rule\": {{ rule }}, \"data\": {{ data }}, \"detector\": {{ detector }}, \"time\": {{ time }} }"
}
```

**Response (`201`):**
```json
{ "name": "generic_webhook" }
```

---

### `POST /plugins`

Loads a plugin with its configuration.

**Request:**
```json
{
  "id": "clickagentic",
  "config": {
    "provider": "openai",
    "model": "gpt-5.2",
    "token": "xxx",
    "from_level": 10
  }
}
```

**Response (`201`):**
```json
{ "id": "clickagentic" }
```

---

## Detectors

### `POST /detector`

Creates and schedules a detector. Requires a datasource. `name` and `for` are required, `rules` (rule file paths) and `webhooks` are optional.

| Field | Default | Description |
|---|---|---|
| `start` | `true` | Run the detector right away. When `false`, the first run happens after `for` |
| `active` | `true` | When `false`, the detector is created paused, resume it with [`POST /detector/{id}/resume`](#post-detectoridresume) |

**Request:**
```json
{
  "name": "5m interval",
  "for": "5m",
  "tenant": "all",
  "description": "detect rules with 5 min interval",
  "webhooks": ["generic_webhook"],
  "data": { "var1": "yy" },
  "start": true
}
```

**Response (`201`):**
```json
{ "id": "abc123" }
```

---

### `GET /detector/list`

Returns all running detectors.

**Response:**
```json
[
  {
    "id": "abc123",
    "name": "5 minute checks",
    "description": "...",
    "tenant": "default",
    "active": true,
    "for_time": "5m",
    "rules_count": 3,
    "webhooks": ["my_webhook"],
    "last_time_exec": "2026-03-16T10:00:00",
    "next_time_exec": "2026-03-16T10:05:00"
  }
]
```

---

### `GET /detector/tenant/{tenant}`

Returns all detectors belonging to a specific tenant.

**Path parameters:**

| Parameter | Description |
|---|---|
| `tenant` | Tenant identifier |

---

### `GET /detector/{id}`

Returns a single detector by job ID.

**Path parameters:**

| Parameter | Description |
|---|---|
| `id` | Detector job ID |

---

### `POST /detector/{id}/stop`

Pauses a detector's scheduled execution.

---

### `POST /detector/{id}/resume`

Resumes a previously paused detector.

---

### `DELETE /detector/{id}`

Removes a detector completely from the scheduler.

---

## Rules

### `POST /rules/{detector_id}`

Adds a rule to a detector. The body uses the same fields as a [rule](rules.md) file. For sigma detectors, send the sigma rule as JSON.

**Path parameters:**

| Parameter | Description |
|---|---|
| `detector_id` | Detector job ID |

**Request:**
```json
{
  "id": "11000000-0000-0000-0000-000000000000",
  "name": "Multiple authentication failures",
  "level": 50,
  "size": ">0",
  "rule": "SELECT * FROM logs WHERE ..."
}
```

**Response (`201`):** the created rule, same format as [`GET /rules/{detector_id}/{rule_id}`](#get-rulesdetector_idrule_id).

---

### `GET /rules/{detector_id}`

Returns all rules loaded in a detector.

**Path parameters:**

| Parameter | Description |
|---|---|
| `detector_id` | Detector job ID |

---

### `GET /rules/{detector_id}/{rule_id}`

Returns a single rule.

**Path parameters:**

| Parameter | Description |
|---|---|
| `detector_id` | Detector job ID |
| `rule_id` | Rule ID (as defined in the rule YAML) |

---

### `GET /rules/{detector_id}/{rule_id}/pause`

Disables a rule (sets `active: false`).

---

### `GET /rules/{detector_id}/{rule_id}/resume`

Re-enables a rule (sets `active: true`).

---

## Errors

Errors of the create routes return `{ "detail": "<message>" }`.

| Status | Description |
|---|---|
| `404` | Datasource, webhook or plugin type not found, or detector not found |
| `409` | Resource already exists, or datasource not configured when creating a detector |
| `422` | Invalid or missing field, invalid template or invalid rule |
| `502` | Connection error to the datasource, webhook or redis, or plugin load error |
