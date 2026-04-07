# Changelog

## [1.5.0] - 2026-04-07

### 🪝 Webhook Changes

- Add slack webhook

- Fix iris webhook support


### 🗃️ Datasource Changes

- Add opensearch datasource

- Elastic minor refactor


### 📝 Documentation

- Add slack documentation

- Add iris documentation

- Update elasticsearch documentation

- Add opensearch documentation


### 🔧 Other changes

- Add new datasource and webhook

- Update readme for new release

## [1.4.0] - 2026-04-05

### 🚀 Features

- Render description field as Jinja2 template

## [1.3.0] - 2026-04-02

### 🐛 Bug Fixes

- Incorrect name for datasource


### 🗃️ Datasource Changes

- Loki minor code refactor

- Add victoria logs support


### 📝 Documentation

- Add victoria logs documentation


### ♻️ Refactor

- Send rule to datasource.

## [1.2.0] - 2026-03-31

### 🚀 Features

- Add sensitive field to not send to webhook


### 🐛 Bug Fixes

- Template are sent in invalid json format


### 📝 Documentation

- Blog post for clickhouse with clickdetect

## [1.1.1] - 2026-03-28

### 🪝 Webhook Changes

- Refactoring the webhook base class


### 🗃️ Datasource Changes

- Refactoring datasource base class

## [1.1.0] - 2026-03-25

### 🚀 Features

- Add verbose option

- Add rule watcher for hot reload


### 🐛 Bug Fixes

- Name is not on result

## [1.0.1] - 2026-03-24

### 🔧 Other changes

- Update uv-build requirement

- Update uv-build requirement from <0.11.0,>=0.10.9 to >=0.10.9,<0.12.0

## [1.0.0] - 2026-03-22

### ⚡ Version 1.0.0

####  🚀 Datasource Changes

- Add loki
- Add clickhouse
- Add postgresql
- Add opensearch/elasticsearch

#### 🪝 Webhook Changes

 - Add e-mail hook
 - Add forgejo hook
 - Add iris hook
 - Add teams hook
 - Add generic hook

#### 🔌 API

- Add api for detectors
- Add api for health check
- Add api for Rules

#### 📝 Documentation

- Create documentation
- Publish documentation to clickdetect.souzo.me

#### by souzo
