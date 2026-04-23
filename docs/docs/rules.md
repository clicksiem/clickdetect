# Rules

Rules are YAML files that define what to query, and under what condition an alert should fire.

## Rule file format

```yaml
id: "001"
name: Brute Force Detected
level: 8
size: ">5"
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
        AND tenant = '{{ detector.tenant }}'
```

## Fields

| Field | Required | Description |
|---|---|---|
| `id` | yes | Unique rule identifier (string) |
| `name` | yes | Human-readable name |
| `level` | yes | Severity level (integer, higher = more severe) |
| `size` | yes | Condition to trigger the alert (see below) |
| `active` | no | Enable or disable the rule (default: `true`) |
| `rule` | yes | Query template (Jinja2, executed against the datasource) |
| `author` | no | List of authors |
| `group` | no | Rule group/category |
| `tags` | no | List of tags for classification |
| `description` | no | Description of what the rule detects |
| `data` | no | Custom key/value data, available in the rule template |

## `size` — condition format

The `size` field compares the **number of rows** returned by the query against a threshold.

| Operator | Example | Meaning |
|---|---|---|
| `>` | `">0"` | At least 1 result |
| `>=` | `">=10"` | 10 or more results |
| `<` | `"<5"` | Fewer than 5 results |
| `<=` | `"<=100"` | 100 or fewer results |
| `==` | `"==1"` | Exactly 1 result |

## Jinja2 templates

The `rule` query is rendered with Jinja2 before execution. The following variables are available:

| Variable | Type | Description |
|---|---|---|
| `detector.name` | string | Detector name |
| `detector.tenant` | string | Tenant identifier |
| `detector.data` | dict | Custom data set in the detector's `data` field |
| `rule.id` | string | Rule ID |
| `rule.name` | string | Rule name |
| `rule.data` | dict | Custom data set in the rule's `data` field |
| `startime` | string | Unix timestamp (int as string) of the interval start |
| `endtime` | string | Unix timestamp (int as string) of the interval end |
| `interval` | string | Detector interval (e.g. `"5m"`) |
| `rule_id` | string | Shorthand for `rule.id` |
| `rule_level` | int | Shorthand for `rule.level` |
| `rule_group` | string | Shorthand for `rule.group` |
| `datasource` | dict | Datasource configuration dict |

### Custom Jinja2 filters

| Filter | Description |
|---|---|
| `\| to_list_like` | Joins items as single-quoted strings: `'a', 'b', 'c'` |
| `\| to_list` | Joins items as comma-separated values: `a, b, c` |
| `\| tojson` | Serializes to JSON (handles datetime, UUID, and dataclasses) |

### Example with template variables

```yaml
rule: |-
    SELECT user, count(*) AS attempts
    FROM auth_logs
    WHERE
        tenant = '{{ detector.tenant }}'
        AND status = 'failed'
        AND timestamp >= now() - INTERVAL 5 MINUTE
    GROUP BY user
    HAVING attempts > {{ rule.data.threshold | default(5) }}
data:
    threshold: 10
```

## Loading rules in a detector

Rules are referenced in the detector's `rules` list. Both direct paths and glob patterns are supported:

```yaml
detectors:
    my_detector:
        rules:
            - "rules/auth/brute_force.yml"
            - "rules/network/*.yml"
            - "rules/**/*.yml"
```

## Webhook alert template variables

When a rule fires and a webhook is called, the following variables are available in the webhook template:

| Variable | Description |
|---|---|
| `rule` | The Rule object (all fields accessible) |
| `data.len` | Number of rows returned by the query |
| `data.value` | List of result rows (each row is a dict) |
| `detector` | The Detector object (name, tenant, data, etc.) |
| `datasource` | The datasource configuration dict |
| `time.startime` | Unix timestamp (float) of the interval start |
| `time.endtime` | Unix timestamp (float) of the interval end |


## Tips

For more precise query results, use the {{ startime }} and {{ endtime }} parameters. These allow you to filter data within a specific time range, making your queries more efficient and relevant

```sql
SELECT
    rule_id,
    rule_description,
    rule_groups
FROM wazuh_alerts
WHERE
    timestamp >= fromUnixTimestamp({{ startime }})
    AND timestamp <= fromUnixTimestamp({{ endtime }});
```
