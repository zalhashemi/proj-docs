---
title: Dependency Inventory
subtitle: "{{project_name}}"
version: 1.0.0
date: "{{YYYY-MM-DD}}"
author: "{{author}}"
project: "{{project_name}}"
doc_id: dependency-inventory
confidential: false
---

<!-- guide: Direct dependencies only (from manifests in scan.dependencies). Licences: read from
installed package metadata (node_modules/<pkg>/package.json, site-packages METADATA) if present
locally; otherwise "unknown". "Outdated" needs a registry check, so without network write
"not checked" rather than guessing. Never guess versions. -->

## Summary

| Ecosystem | Manifest | Runtime deps | Dev deps |
|---|---|---|---|
| {{npm/pip/go}} | `{{file}}` | {{n}} | {{n}} |

## Runtime dependencies

| Package | Declared version | Licence | Purpose | Flags |
|---|---|---|---|---|
| {{name}} | `{{range}}` | {{licence or unknown}} | {{one-line purpose}} | {{e.g. copyleft, unpinned, deprecated}} |

## Development dependencies

| Package | Declared version | Licence | Purpose |
|---|---|---|---|
| {{name}} | `{{range}}` | {{licence}} | {{purpose}} |

## Flags

<!-- guide: Unpinned (*, latest), git/URL deps, copyleft licences (GPL/AGPL) in a proprietary
project, packages known to be deprecated. Explain each in one line. -->

- {{flag}}

## How to audit

```bash
{{npm audit / pip-audit / govulncheck / cargo audit}}  ⟨untested⟩
```

## Related documents

[Security Threat Model](security-threat-model.md)

## Assumptions and open questions

| # | Item | Type | Why unverified | Who can confirm |
|---|------|------|----------------|-----------------|
| A1 | {{item}} | assumption | {{reason}} | {{role}} |
