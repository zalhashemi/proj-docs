---
title: CI/CD and Deployment
subtitle: "{{project_name}}"
version: 1.0.0
date: "{{YYYY-MM-DD}}"
author: "{{author}}"
project: "{{project_name}}"
doc_id: cicd-deployment
confidential: false
---

<!-- guide: Pipelines from CI config files (scan.ci). Deployment targets from infra files
and platform configs. If there's no deploy config, say "No deployment automation found in the
repo" and describe the manual path only if the user provided it. -->

## Pipelines

| Pipeline | File | Trigger | Jobs |
|---|---|---|---|
| {{name}} | `{{.github/workflows/x.yml}}` | {{push/PR/tag}} | {{jobs}} |

```mermaid
flowchart LR
  push[Push / PR] --> lint[Lint] --> test[Test] --> build[Build] --> deploy[Deploy]
```

## Environments

| Environment | URL | Deployed from | How |
|---|---|---|---|
| {{env}} | {{url}} ⟨assumption⟩ | {{branch/tag}} | {{mechanism}} |

## Release process

<!-- guide: How a version is cut (tags, release workflow, changelog tooling). -->

1. {{step}}

## Rollback

<!-- guide: Concrete commands for the platform found (e.g. kubectl rollout undo, redeploy previous
image tag, vercel rollback). Mark commands not verifiable from the repo ⟨untested⟩. -->

```bash
{{rollback command}}
```

## Secrets in CI

<!-- guide: Names only (from `secrets.X` references in workflows). Never values. -->

| Secret name | Used by | Purpose |
|---|---|---|
| `{{NAME}}` | `{{workflow}}` | {{purpose}} |

## Related documents

[Runbook](runbook.md) · [Environment and Configuration Reference](env-config-reference.md)

## Assumptions and open questions

| # | Item | Type | Why unverified | Who can confirm |
|---|------|------|----------------|-----------------|
| A1 | {{item}} | assumption | {{reason}} | {{role}} |
