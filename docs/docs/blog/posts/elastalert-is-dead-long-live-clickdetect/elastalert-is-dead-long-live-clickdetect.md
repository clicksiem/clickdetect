---
authors:
    - souzo
categories:
    - siem
    - clickhouse
    - alerting
    - blog
    - clickdetect
    - security
tags:
    - clickhouse
    - clickdetect
date: 2026-04-19
pin: false
---

# ElastAlert is dead, long live Clickdetect

Hey, souzo here.

ElastAlert has been around for a long time and served the security community well. But the ecosystem has changed — new datasources emerged, new integrations became standard, and the expectations around alerting tools grew significantly. ElastAlert has struggled to keep up.

This post introduces **Clickdetect** as a modern alternative: more datasources, more webhooks, more control over your queries, and a simpler operational model. If you are tired of working around ElastAlert's limitations, this is for you.

Clickdetect is a generic alerting and detection engine that supports any datasource you have and integrates with any webhook you want.

Check it out on GitHub: [https://github.com/clicksiem/clickdetect](https://github.com/clicksiem/clickdetect).

You can also read my previous blog post about [Building a powerful SIEM with Clickhouse and Clickdetect](https://medium.com/@souzo/building-a-powerful-siem-with-clickhouse-and-clickdetect-ae68a4495a76).

# Why replace ElastAlert with Clickdetect?

You may think — who is this guy trying to tell me that Clickdetect is better than ElastAlert when I've been using ElastAlert for years?

I'm just someone trying to build the best open source security project of my life.

Let me show you why this approach is better.

First of all, let me explain why you should choose Clickhouse instead of Elasticsearch.

## Why replace Elasticsearch

See this Clickhouse post: [Clickhouse Vs Elasticsearch](https://clickhouse.com/blog/clickhouse_vs_elasticsearch_the_billion_row_matchup)
I tested and I'm current running in a closed environment. I can guarantee, everything Clickhouse posted is real, and it's even better.

### Scalability

* Clickhouse scales better than OpenSearch/Elasticsearch with **Distributed** tables.
* You can use big data schemas to centralize your data without being limited to your current storage.

### Big data standard schemas | Data lakehouse

You can create your own big data table using Apache Iceberg, Delta Lake, Hudi, etc.

This approach gives you a better way to store your data (I recommend Delta Lake by Databricks).

You can also integrate any data lake you already have with big data tables!

### Better storage cost

* You can cut your disk usage by **90%** with Clickhouse while maintaining the same (or better) performance, thanks to its built-in compression.
* **90%** of disk usage reduction, are you crazy, this means your 1 Petabyte storage will be 100 terabyte usage storage!

### More control

* You have full control over your data — Clickhouse is like PostgreSQL, but built for your dreams.

### More, more, more

* Reading the Clickhouse documentation is a piece of heaven — you will discover functionalities you never knew existed!
* WARNING: You could become addicted!

## Ok, Clickhouse is better — but why Clickdetect over ElastAlert?

I built Clickdetect to be as generic as possible. You can even use Clickdetect with Elasticsearch if you are not ready to switch to Clickhouse as your datasource.

### Datasource integrations

* Elasticsearch/Opensearch: Yes, Clickdetect has integration with it.
* Clickhouse: Of course.
* Loki: Grafana Loki datasource integration — great if you want to replace Loki or the Grafana alerting engine.
* VictoriaLogs: VictoriaLogs can match the performance of Elasticsearch and Clickhouse. I simply didn't choose it as the primary datasource because it is still very recent.
* PostgreSQL: PostgreSQL integration — you can search through your database. If you use TimescaleDB or TigerData, this works great too.
* Databricks (not implemented yet, but on my roadmap).

### Webhooks

* Generic: Generic integration — send to any webhook, including N8N.
* DFIR Iris: Send alerts to DFIR Iris.
* Forgejo/Gitea: Create issues from your alerts.
* Email: Send alerts via e-mail.
* Microsoft Teams: Send alerts to Microsoft Teams.
* Slack: Send alerts to Slack.
* Telegram: Send alerts to a Telegram bot.
* Whatever you want: The Clickdetect documentation will show you how to implement your own webhook — or just open an issue!

### Runtime management

* You can use the **reload** option in Clickdetect to hot-reload your rules whenever a new rule is added to disk.
* API: Clickdetect has an API to manage it programmatically.

### You write your rules

* Clickdetect is built to be simple. **You write your query**, and Clickdetect handles the rest.

## ElastAlert rules vs Clickdetect rules

Let's make this concrete. Here is the same detection — **multiple failed logins in a short window** — written in both tools. This example uses **Elasticsearch/OpenSearch as the datasource**, so if you are already an ElastAlert user, you can migrate without touching your stack.

### ElastAlert

```yaml
name: Multiple Failed Logins
type: frequency
index: wazuh-alerts-*
num_events: 15
timeframe:
  minutes: 5
filter:
  - term:
      rule.groups: "authentication_failed"
  - term:
      data.win.system.eventID: "4625"
alert:
  - slack
slack_webhook_url: "https://hooks.slack.com/services/your/webhook/url"
```

ElastAlert owns the query logic. You configure *what* you want to detect through its abstraction layer — frequency, spike, flatline — and it builds the query for you. That works until you need something it does not support.

### Clickdetect

**runner.yml** — your datasource and detector configuration:

```yaml
datasource:
    type: elasticsearch
    url: http://localhost:9200
    index: wazuh-alerts-*
    username: elastic
    password: changeme

webhooks:
    slack:
        type: slack
        url: "https://hooks.slack.com/services/your/webhook/url"

detectors:
    5m_detector:
        for: "5m"
        rules:
            - "rules/windows/*.yml"
        webhooks:
            - slack
```

**rules/windows/multiple_failed_logins.yml** — the rule itself:

```yaml
id: "a1b2c3d4-0000-0000-0000-000000000001"
name: "Windows - Multiple Authentication Failures"
level: 12
size: ">0"
active: true
rule: |-
    {
        "size": 0,
        "query": {
            "bool": {
                "filter": [
                    { "term": { "rule.groups": "authentication_failed" } },
                    { "term": { "data.win.system.eventID": "4625" } },
                    { "range": { "@timestamp": { "gte": "now-5m" } } }
                ]
            }
        },
        "aggs": {
            "by_user": {
                "terms": { "field": "data.win.eventdata.targetUserName", "min_doc_count": 15 }
            }
        }
    }
```

With Clickdetect, **you write the query directly** in Elasticsearch Query DSL. No abstraction layer, no hidden magic. If Elasticsearch can do it, Clickdetect can detect it.

---

The migration path is straightforward: keep your Elasticsearch/OpenSearch stack, swap ElastAlert for Clickdetect, and start writing your own queries. When you are ready to move to Clickhouse, it is just a datasource change in `runner.yml`.

# Conclusion

If you made it this far, you now know why I built Clickdetect and what it can do for you.

Clickdetect is open source, actively maintained, and designed to grow with your infrastructure — whether you are running Elasticsearch today or planning a full move to Clickhouse tomorrow.

If this project helped you or sounds promising, **please give it a star on GitHub** — it means a lot and helps the project reach more people in the security community.

[⭐ Star Clickdetect on GitHub](https://github.com/clicksiem/clickdetect)

Have questions, ideas, or want to contribute? Open an issue or a pull request — the door is always open.
