# High Availability

By default Clickdetect runs as a single process: detector scheduling state (the
detection window per detector) lives in memory. Running two instances against
the same config would make both evaluate the same detectors, producing
**duplicate alerts**, and a restart would lose the window state, causing gaps or
reprocessing.

Configuring **Redis** turns Clickdetect into an active-passive, multi-replica
setup with automatic failover — no separate leader election required.

## How it works

Each detector uses a shared **store** for two things:

- **A distributed lock**, acquired at the start of every detector run. Only one
  replica acquires the lock for a given detector window; the others skip that
  cycle. This is what prevents duplicate alerts across replicas.
- **The detection window** (`last_time`), kept in Redis instead of memory. When a
  replica takes over after a failover or restart, it resumes from the exact same
  window, so no time range is missed or evaluated twice.

```
   ┌──────────┐   ┌──────────┐   ┌──────────┐
   │ replica 1│   │ replica 2│   │ replica 3│   same runner.yml on every replica
   └────┬─────┘   └────┬─────┘   └────┬─────┘
        └──────────────┼──────────────┘
                 ┌──────▼──────┐
                 │    Redis    │  per-detector lock + shared last_time
                 └─────────────┘
```

Without a `redis` block, Clickdetect falls back to an in-process store and
behaves exactly as a single-node deployment.

## Configuration

Add an optional top-level `redis` block to your [runner](runner.md):

```yaml
redis:
    url: redis://localhost:6379/0
    namespace: clickdetect
    lock_ttl: 1500
```

| Field | Required | Default | Description |
|---|---|---|---|
| `url` | yes | — | Redis connection URL |
| `namespace` | no | `clickdetect` | Prefix for all keys (lock and window state) |
| `lock_ttl` | no | `1500` | Lock lifetime in seconds (must be > 0) |

Run identical replicas, all pointing at the same `runner.yml` and the same
Redis instance. If a replica dies, another picks up the next detector cycle
automatically.

### About `lock_ttl`

While a detector runs, a background watchdog **renews the lock** (every
`lock_ttl / 3`), so a run may take longer than `lock_ttl` without ever losing
the lock — no duplicate alerts even for slow queries. You do **not** need to
size `lock_ttl` above your slowest run.

Instead, `lock_ttl` is the **failover latency**: if a replica crashes mid-run,
no one renews the lock, so it expires after at most `lock_ttl` seconds and
another replica takes over that detector. Smaller values fail over faster at the
cost of slightly more Redis traffic; larger values are lighter but leave a dead
replica's detectors idle for longer.

!!! note
    If a lock is lost anyway (e.g. a Redis outage outlasting the watchdog), a
    warning is logged and the next cycle self-heals.

## Keys

For a detector identified by `tenant:name:for`, Clickdetect uses:

- `"{namespace}:lock:{tenant}:{name}:{for}"` — the distributed lock
- `"{namespace}:win:{tenant}:{name}:{for}"` — the last processed window time
