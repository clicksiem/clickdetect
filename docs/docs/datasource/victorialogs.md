# VictoriaLogs

Query log streams from VictoriaLogs.

!!! warning
    This datasource integration has not been fully validated yet. If you use it successfully (or run into issues), please [open an issue](https://github.com/clicksiem/clickdetect/issues).

## Config

```yaml
datasource:
    type: victorialogs                  # required
    url: http://localhost:9428          # required
    username: admin                     # optional
    password: pass                      # optional
    verify: false                       # optional default(false) — verify SSL certificate
    account_id: '0'                     # optional — sets X-VictoriaMetrics-Account-Id header
    project_id: '0'                     # optional — sets X-VictoriaMetrics-Project-Id header
```

## Notes

- The `rule` query must be a valid [LogsQL](https://docs.victoriametrics.com/victorialogs/logsql/) expression (e.g. `_msg:error`).
- Results are fetched via `/select/logsql/query` with a limit of 5000 log lines.
- The result count (`data.len`) is the total number of log lines returned.
- Each result row is a parsed JSON object from the NDJSON response.
- `account_id` and `project_id` are used for multi-tenancy in VictoriaMetrics enterprise setups.
