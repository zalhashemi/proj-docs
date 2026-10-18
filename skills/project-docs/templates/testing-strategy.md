---
title: Testing Strategy
subtitle: "{{project_name}}"
version: 1.0.0
date: "{{YYYY-MM-DD}}"
author: "{{author}}"
project: "{{project_name}}"
doc_id: testing-strategy
confidential: false
---

<!-- guide: Describe current reality from scan.tests (frameworks, locations, counts, coverage
config) then the gaps. Don't claim a coverage number unless a coverage report/config shows it. -->

## Current state

| Layer | Framework | Location | Approx. tests | Runs in CI |
|---|---|---|---|---|
| Unit | {{framework}} | `{{path}}` | {{n}} | {{yes/no}} |
| Integration | | | | |
| End-to-end | | | | |

Coverage: {{config + threshold if present, else "not configured"}}

## How to run

```bash
{{all tests}}
{{single file / watch mode}}
{{coverage}}
```

## What to test where

<!-- guide: Practical rules for this codebase: which layer catches which bugs; cite a good
existing test file as the pattern to copy. -->

| Change | Test type | Example to copy |
|---|---|---|
| {{e.g. new endpoint}} | {{integration}} | `{{path}}` |

## Gaps and priorities

<!-- guide: Areas with code but no tests (compare source dirs to test dirs), critical paths
(auth, payments, data writes) without tests. -->

| Area | Risk | Suggested tests | Priority |
|---|---|---|---|
| `{{path}}` | {{risk}} | {{tests}} | {{H/M/L}} |

## Targets

- Coverage target: {{coverage_target}}
- {{other targets}}

## Related documents

[CI/CD and Deployment](cicd-deployment.md) · [Developer Guide](dev-guide.md)

## Assumptions and open questions

| # | Item | Type | Why unverified | Who can confirm |
|---|------|------|----------------|-----------------|
| A1 | {{item}} | assumption | {{reason}} | {{role}} |
