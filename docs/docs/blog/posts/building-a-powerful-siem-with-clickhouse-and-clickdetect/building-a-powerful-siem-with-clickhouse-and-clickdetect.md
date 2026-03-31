---
authors: 
    - souzo
categories:
    - siem
    - clickhouse
    - alerting
    - blog
    - wazuh
    - clickdetect
    - security
tags:
    - clickhouse
date: 2026-03-30
pin: false
---

# Building a powerful SIEM with Clickhouse and Clickdetect

Hi everyone, souzo here. In this blog post I will walk you through building a base SIEM architecture capable of generating security alerts.

This post will not cover how to collect data into Clickhouse. Instead, I will focus on a base table schema for receiving logs and performing detection with Clickdetect.

In a future post, I will show you how to use Wazuh to send data to any datasource and leverage Clickdetect to power Wazuh detections.

<video width="640" controls>
    <source src="/assets/clickdetect-runner-demo.mp4" type="video/mp4">
</video>

## Why Clickhouse instead ElasticSearch

I'm not sponsored by Clickhouse, but I love this database, you can do everything you want and use it in any situation.

I thought about this many times, and this is why I prefer Clickhouse instead of ElasticSearch for log management.

1. Log data is parsed and decoded, so logs can be stored as JSON. Clickhouse is awesome at searching JSON data: [look at this post](https://clickhouse.com/blog/json-data-type-gets-even-better);
2. Clickhouse can decrease disk usage by 90% and deliver the same or better performance than Elastic/OpenSearch;
3. Clickhouse can perform full-text search and you can create better indexes for logs;
4. More control of data. You can do anything in clickhouse and use it for any situation you might have;
5. Scalability. Take a look in [distributed table](https://clickhouse.com/docs/engines/table-engines/special/distributed);
6. Storage
    - You can use hybrid storage like Host/Amazon S3 or only Host or S3;
    - You can encrypt data to be compliance;
    - Tables in clickhouse are compressed by default
7. SQL ( Do I need to say anything? )


### Companies that use Clickhouse

1. Huntress
2. RunReveal
3. Exabeam
4. Fortinet (FortiSIEM)
5. Cloudflare


## Architecture

A basic architecture how this will work.

![Diagram overview](/assets/post-clickhouse-clickdetect.png)

1. Logs are sent by assets to wazuh;
2. Wazuh decodes and send parsed logs to Clickhouse;
3. Clickdetect will be scheduled to detect and generate alerts;
4. Alerts are sent to a webhook.

## Clickhouse Wazuh Schema

This schema is for Wazuh Alerts. In this case, Wazuh is only a log collector — we will only need Wazuh's decoder capabilities.

#### Database 

```sql
CREATE DATABASE IF NOT EXISTS siem
```

#### Table

```sql
CREATE TABLE IF NOT EXISTS siem.wazuh_alerts (
    id UUID default generateUUIDv7() CODEC(ZSTD(1)),
    timestamp DateTime64(6) DEFAULT now() CODEC(DoubleDelta),
    retention UInt16 DEFAULT 30,
    tenant LowCardinality(String) CODEC(ZSTD(1)),
    rule_id UInt32 CODEC(Delta(8), ZSTD(1)),
    rule_description String CODEC(ZSTD(1)),
    rule_groups Array(LowCardinality(String)) CODEC(ZSTD(1)),
    rule_level UInt8,
    agent_id UInt16,
    agent_name String CODEC(ZSTD(1)),
    manager LowCardinality(String) CODEC(ZSTD(1)),
    agent_ip String CODEC(ZSTD(1)),
    full_log String CODEC(ZSTD(22)),
    message String CODEC(ZSTD(22)),
    srcuser String CODEC(ZSTD(1)),
    dstuser String CODEC(ZSTD(1)),
    srcip String CODEC(ZSTD(1)),
    dstip String CODEC(ZSTD(1)),
    hostname String CODEC(ZSTD(1)),
    location String CODEC(ZSTD(1)),
    decoder LowCardinality(String) CODEC(ZSTD(1)),
    action LowCardinality(String) CODEC(ZSTD(1)),
    protocol LowCardinality(String) CODEC(ZSTD(1)),
    status LowCardinality(String) CODEC(ZSTD(1)),
    alert JSON CODEC(ZSTD(1)),

    INDEX idx_full_log full_log TYPE tokenbf_v1(32768, 3, 0) GRANULARITY 1,
    INDEX idx_rule_description rule_description TYPE tokenbf_v1(8192, 3, 0) GRANULARITY 1,
    INDEX idx_rule_groups rule_groups TYPE bloom_filter(0.01) GRANULARITY 1
)
engine = MergeTree
partition by (toYYYYMMDD(timestamp), tenant)
order by (tenant, toUnixTimestamp(timestamp), id)
TTL timestamp + toIntervalDay(retention)
settings
    index_granularity = 4096,
    ttl_only_drop_parts = 1,
    storage_policy = 'your_s3_policy'
```

## Performing detection with clickdetect

To perform detection in clickhouse, we need to create our runner

### Runner

#### Define datasource

```yaml
datasource:
    type: clickhouse
    host: <clickhouse ip>
    port: 8123
    verify: false
    username: default
    password: default
    database: siem
```

#### Define webhook

```yaml
webhooks:
    webhook_name:
        type: generic
        url: http://<webhook_host>/
```

#### Define detector

```yaml
detectors:
    detector_N:
        name: "Detector name"
        description: "Detector description"
        for: 5m # detector time (s, m, h, d)
        rules:
            - "detect_test.yml" # you can use * for match directory
        data:
            var1: "my var"
```

### Rule

```yaml
id: "00000000-0000-0000-0000-000000000000"
name: "Detect all data in clickhouse"
level: 1
size: ">0"
author: 
    - Vinicius Morais <me@souzo.me>
rule: |-
    SELECT * FROM wazuh_alerts LIMIT 100;
```

### Clickdetect

```sh
uv run clickdetect -r runner.yml
```

## Conclusion

With just a Clickhouse table, a runner configuration, and a detection rule, you have the foundation of a functional SIEM. This architecture is lightweight, cost-effective, and scales well — whether you're running it on a single node or a distributed Clickhouse cluster.

The key advantage over traditional SIEM solutions is control: you own the data, you define the schema, and you write the detections in plain SQL. There are no vendor lock-ins, no per-GB ingestion fees, and no black-box detection engines.

**Rule**: more rules examples you can found [here](https://github.com/clicksiem/clickdetect/tree/main/example_rules)

## Next Steps

This post covered the base architecture. Here is what comes next:

- **Part 2 — Wazuh + Clickdetect**: How to configure Wazuh to forward decoded alerts directly to Clickhouse, and how to write detection rules that leverage Wazuh's decoded fields.
- **Alerting pipelines**: Routing alerts to Slack, PagerDuty, or a ticketing system using Clickdetect webhooks.
- **Multi-tenancy**: Using the `tenant` field to isolate data between clients or business units in a single Clickhouse cluster.

Follow along on [GitHub](https://github.com/clicksiem/clickdetect) and feel free to open issues or contribute detection rules.
