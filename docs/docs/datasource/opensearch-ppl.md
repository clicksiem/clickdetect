# Opensearch PPL

Query events from Opensearch using the
[Piped Processing Language (PPL)](https://opensearch.org/docs/latest/search-plugins/sql/ppl/index/),
served by the SQL/PPL plugin.

Unlike the [Opensearch](opensearch.md) datasource — which sends Query DSL to a fixed
index — a PPL query carries its own `source=` index pattern, so a single datasource can
search across any index.

## Config

```yaml
datasource:
    type: opensearch-ppl        # required
    url: http://localhost:9200  # required
    username: admin             # optional
    password: pass              # optional
    verify: false               # optional default(false) — verify SSL certificate
```

## Notes

- Queries are sent as `POST /_plugins/_ppl`. The SQL/PPL plugin must be installed
  (it ships with Opensearch by default).
- There is no `index` setting — the index pattern comes from the query itself.
- Authentication is optional and uses basic `username`/`password`.
- The `rule` query must be a valid PPL statement.
- The result count (`data.len`) is the `size` field returned by the API.
- Each result row maps the response `schema` column names onto the `datarows` values.
- On connect the datasource checks `/_cluster/health`; an unhealthy cluster is logged
  and the query is retried on the next run.

## Example

```yaml
rule: |-
    source=wazuh-alerts-* | where `rule.id` = '502'
```

## Sigma

Sigma rules are converted with the `opensearch-ppl` pySigma backend, so a rule marked
`sigma: true` is translated to PPL before it is sent. See [Sigma](../sigma.md) for the
different ways to enable it.

The backend reads optional attributes from the rule's `custom` block:

| Attribute | Description |
| --- | --- |
| `opensearch_ppl_index` | Index pattern to use instead of the one derived from `logsource` |
| `opensearch_ppl_time_field` | Timestamp field used for the time range |
| `opensearch_ppl_min_time` | Start of the time range (e.g. `-5m`) |
| `opensearch_ppl_max_time` | End of the time range (e.g. `now`) |

```yaml
title: "wazuh opensearch sigma test - Manager Started"
status: test
id: 32bc608c-67ab-4d58-8361-35d3baac726c
logsource:
    product: wazuh
    category: indexer
detection:
    sel:
        rule_id: 502
    condition: 1 of sel
custom:
    opensearch_ppl_index: "wazuh-alerts-*"
    opensearch_ppl_min_time: "-5m"
    opensearch_ppl_max_time: "now"
```

!!! tip
    Keep the rule's time range aligned with the detector's `for` interval, otherwise the
    same events are matched on every run.

See the blog post
[Extending Wazuh detection capabilities with clickdetect, Opensearch PPL and Sigma Rules](../blog/2026/05/26/extending-wazuh-detection-capabilities-with-clickdetect-opensearch-ppl-and-sigma-rules/)
for a full walkthrough.
