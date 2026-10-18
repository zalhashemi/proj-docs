---
title: Release Notes
subtitle: "{{project_name}}"
version: 1.0.0
date: "{{YYYY-MM-DD}}"
author: "{{author}}"
project: "{{project_name}}"
doc_id: release-notes
confidential: false
---

<!-- guide: Source priority: CHANGELOG > git tags + commit subjects between tags. Rewrite commit
subjects into user-facing language and drop internal noise (chore, ci, refactor) unless
relevant. Newest first. No tags → group by month and say so. -->

## {{version}} ({{date}})

### New

- {{feature}}

### Improved

- {{improvement}}

### Fixed

- {{fix}}

### Breaking changes

- {{change}}. See [Upgrade and Migration Guide](upgrade-migration-guide.md).

## {{previous version}} ({{date}})

{{…}}

## Related documents

[Upgrade and Migration Guide](upgrade-migration-guide.md)

## Assumptions and open questions

| # | Item | Type | Why unverified | Who can confirm |
|---|------|------|----------------|-----------------|
| A1 | {{item}} | assumption | {{reason}} | {{role}} |
