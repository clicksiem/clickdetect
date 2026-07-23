# Databricks

Query alerts from a [Databricks](https://www.databricks.com/) SQL warehouse, using it as
the SQL engine on top of your lakehouse tables.

## Config

```yaml
datasource:
    type: databricks                    # required
    host: adb-xxx.azuredatabricks.net   # required — workspace hostname
    path: /sql/1.0/warehouses/xxxx      # required — HTTP path of the SQL warehouse
    token: dapiXXXXXXXX                 # required — personal access token
    catalog: my_catalog                 # optional — Unity Catalog name
```

`host` and `path` are the **Server hostname** and **HTTP path** shown under the
*Connection details* tab of the SQL warehouse in the Databricks UI.

## Notes

- The `rule` query must be valid
  [Databricks SQL](https://docs.databricks.com/aws/en/sql/language-manual/).
- The result count (`data.len`) is the number of rows returned by the query.
- `token` is a sensitive field and should be stored securely (e.g. via environment
  variable substitution).
- `catalog` is optional; when omitted the warehouse's default catalog is used. Tables can
  also be fully qualified in the query (`catalog.schema.table`).
- A failed query closes the connection, which is reopened on the next run — a warehouse
  that is starting up will not permanently break the detector.

## Example

```yaml
rule: |-
    SELECT * FROM main.security.wazuh_alerts
    WHERE timestamp >= current_timestamp() - INTERVAL 5 MINUTES
      AND rule_id = '502'
```

!!! tip
    Serverless SQL warehouses auto-suspend when idle and take a few seconds to resume.
    Align the detector `for` interval with the warehouse auto-stop setting to avoid
    paying for a warehouse that is woken up on every run.
