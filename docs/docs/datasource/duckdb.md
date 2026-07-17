# DuckDB

Query alerts with [DuckDB](https://duckdb.org/), an in-process SQL engine. Run
queries against an in-memory database, a local `.duckdb` file, or remote data in
S3-compatible object storage (S3, Cloudflare R2, Google Cloud Storage) — including
data lakes via functions like `delta_scan` and `read_parquet`.

## Config

```yaml
datasource:
    type: duckdb          # required
    database: ":memory:"  # optional default(":memory:") — ":memory:" or path to a .duckdb file
    s3_key: KEYID         # optional — access key id (enables the S3 secret when set)
    s3_secret: SECRET     # optional — secret access key
    s3_host: s3.amazonaws.com  # optional default("s3.amazonaws.com") — endpoint
    s3_region: us-east-1  # optional default("us-east-1")
    s3_type: s3           # optional default("s3") — one of: s3, gcs, r2
    r2_account: ACCOUNTID # optional — Cloudflare R2 account id (only for s3_type: r2)
    ssl: true             # optional default(true) — use SSL for object storage
    verify: true          # optional default(true) — verify SSL certificates
```

## Notes

- The `rule` query must be valid DuckDB SQL.
- The result count (`data.len`) is the number of rows returned by the query.
- `database: ":memory:"` opens a fresh in-memory database. Any other value is
  treated as a file path and is opened **read-only**.
- Object storage is configured only when `s3_key` is set; a DuckDB secret is then
  created from the `s3_*` settings. `s3_type` must be one of `s3`, `gcs`, or `r2`.
- `r2_account` is only used when `s3_type: r2`.
- `s3_secret` is a sensitive field and should be stored securely (e.g. via
  environment variable substitution).

## Example: query a Delta Lake table

```yaml
rule: |-
    SELECT * FROM delta_scan("s3://my-bucket/logs")
    WHERE timestamp >= now() - interval 5 minute
      AND win.data.eventID = '4720'
```

!!! note
    `delta_scan` requires DuckDB's `delta` extension. DuckDB auto-installs and
    loads official extensions on first use when it has internet access. In an
    offline/air-gapped environment, install it beforehand with
    `INSTALL delta; LOAD delta;`.

See the blog post
[Advanced security alerting with DuckDB and Delta Lake](../blog/2026/07/17/advanced-security-alerting-with-duckdb-and-delta-lake/)
for a full walkthrough.
