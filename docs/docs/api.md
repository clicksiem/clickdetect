# API

The REST API is enabled with the `--api` flag. It runs on port `8080` by default (override with `-p`).

```sh
uv run clickdetect --api -p 8080
```

## Health

### `GET /health/ok`

Returns a simple liveness check.

**Response:**
```json
{ "ok": true }
```

---

## Detectors

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
