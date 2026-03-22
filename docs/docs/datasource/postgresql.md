# PostgreSQL

> PostgreSQL is under testing

Query alerts from a PostgreSQL database.

## Config

```yaml
datasource:
    type: postgresql # required
    host: localhost  # required
    port: 5432       # optional default(5432)
    username: user   # required
    password: pass   # required
    database: mydb   # required
```

## Notes

- The `rule` query must be valid SQL.
- The result count (`data.len`) is the number of rows returned by the query.
- Uses a connection pool internally (`asyncpg`).
