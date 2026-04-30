# Databricks

Query alerts from a Databricks SQL warehouse.

## Config

```yaml
datasource:
    type: databricks      # required
    host: adb-xxx.azuredatabricks.net  # required — Databricks workspace hostname
    path: /sql/1.0/warehouses/xxx      # required — HTTP path of the SQL warehouse
    token: dapiXXXXXXXX  # required — personal access token
    catalog: my_catalog   # optional — Unity Catalog name
```

## Notes

- The `rule` query must be valid SQL.
- The result count (`data.len`) is the number of rows returned by the query.
- `token` is a sensitive field and should be stored securely (e.g. via environment variable substitution).
- `catalog` is optional; when omitted, the warehouse's default catalog is used.
