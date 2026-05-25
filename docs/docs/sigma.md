# Sigma

Clickdetect supports sigma rules. Checkout [https://github.com/clicksiem/sigma_rules](https://github.com/clicksiem/sigma_rules) for rules in clickdetect format.

Has 3 ways to run sigma rules

### Way 1 run with clickdetect

This way assume that all discovered rules are sigma

- `uv run clickdetect --sigma`

### Way 2 create a rule with `sigma: true`

This way will parse sigma rule inside "rule"

```yml
id: "000000000"
name: "Rule example"
level: 10
size: ">0"
active: true
sigma: true # goes here
author: 
    - Vinicius Morais <me@souzo.me>
group: test
tags: 
    - test
rule: |-
    <your sigma rule here>
```

### Way 3, configure in runner.yml

This way assumes that all rules loaded from the detector will be treated as a sigma rules.

```yml
detectors:
    detector_name:
        name: "5m interval"
        for: "5m"
        description: "detect rules with 5 min interval"
        rules:
            - "test.yml"
        webhooks:
            - generic_webhook
        sigma: true # here
```
