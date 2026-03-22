# ClickHouse

Query alerts from a ClickHouse database.

## Config

```yaml
datasource:
    type: clickhouse # required
    host: localhost  # required
    port: 8123       # required
    username: default # required
    password: pass   # required
    database: default # optional default("default")
    verify: false    # optional default(false) — enable TLS
```

## Notes

- The `rule` query must be valid SQL.
- `verify: true` enables secure (TLS) connection.
- The result count (`data.len`) is the number of rows returned by the query.
