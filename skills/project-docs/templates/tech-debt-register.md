---
title: Tech Debt Register
subtitle: "{{project_name}}"
version: 1.0.0
date: "{{YYYY-MM-DD}}"
author: "{{author}}"
project: "{{project_name}}"
doc_id: tech-debt-register
confidential: false
---

<!-- guide: Sources: TODO/FIXME/HACK/XXX/"shortcut:" comments (group duplicates), very large
files, untested critical modules, deprecated deps, duplicated code you can see. Every item
cites a path. Effort and impact are judgements, so say so in the method line. -->

## Method

Items come from code markers, file size and test gaps found in the repo. Impact and effort
are reviewer estimates (S/M/L).

## Register

| ID | Item | Location | Impact | Effort | Priority | Suggested fix |
|---|---|---|---|---|---|---|
| TD-1 | {{item}} | `{{path:line}}` | {{H/M/L}} | {{S/M/L}} | {{P1–P3}} | {{fix}} |

## Code markers

| Marker | Count | Top locations |
|---|---|---|
| TODO | {{n}} | `{{paths}}` |
| FIXME | {{n}} | |

## Quick wins

<!-- guide: High impact + small effort items. -->

- {{item}}

## Related documents

[Risk Register](risk-register.md)

## Assumptions and open questions

| # | Item | Type | Why unverified | Who can confirm |
|---|------|------|----------------|-----------------|
| A1 | {{item}} | assumption | {{reason}} | {{role}} |
