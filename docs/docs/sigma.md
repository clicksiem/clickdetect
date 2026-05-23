# Sigma

Has 2 ways to run sigma rules

### Way 1 run with clickdetect

- `uv run clickdetect --sigma`

### Way 2 create a rule with `sigma: true`

```
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
