---
authors: 
    - souzo
categories:
    - announcement
    - release
tags:
    - announcement
    - release
date: 2026-05-25
---

# Version 1.14.0 changelog
# Changelog

## [1.14.0] - 2026-05-25

### 🚀 Features

- Add sigma backend system by @souzomain
- Add opensearch sigma rules backend by @souzomain
- Add opensearch PPL sigma rules backend by @souzomain
- *(sigma)* Add new sigma option to threat all rules discovered as sigma by @souzomain
- *(sigma)* Add loki sigma backend support by @souzomain
- *(docs)* Add opensearch ppl documentation by @souzomain

### 🐛 Bug Fixes

- Fix endpoint mismatch the correct is `_ppl` not `_sql` by @souzomain
- Invalid condition causing rule not load by @souzomain
- Fixed error while rule is updated with neovim (delete + create) by @souzomain

### 🗃️ Datasource Changes

- *(datasource)* Add opensearch PPL datasource by @souzomain
- *(datasource)* Add new option to handle sigma rules in datasource by @souzomain

### 🔧 Other changes

- *(other)* Add `uv.lock` to the project by @souzomain

#### by souzo
