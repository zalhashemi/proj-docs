---
title: Environment and Configuration Reference
subtitle: "{{project_name}}"
version: 1.0.0
date: "{{YYYY-MM-DD}}"
author: "{{author}}"
project: "{{project_name}}"
doc_id: env-config-reference
confidential: false
---

<!-- guide: NEVER include real values of secrets. Show variable NAMES, type, purpose, required,
and a safe example only for non-secrets (ports, log levels, public URLs like localhost).
If a committed file contains a token-like value, write «redacted» and add a WARNING callout. -->

> [!WARNING]
> This document lists configuration names only. Real secret values live in {{secret store ⟨assumption⟩}} and must never be committed.

## Environment variables

<!-- guide: From scan.env_vars (union of .env.example, config files, code references). Required =
read without a default in code. Source = where it's read. Group by area if > 15. -->

| Name | Type | Required | Default | Purpose | Read in |
|---|---|---|---|---|---|
| `{{NAME}}` | {{string/int/bool/url}} | {{yes/no}} | {{safe default or —}} | {{purpose}} | `{{file}}` |

## Configuration files

| File | Format | Purpose |
|---|---|---|
| `{{path}}` | {{yaml/json/toml}} | {{purpose}} |

## Feature flags

<!-- guide: From flag libs (LaunchDarkly, Unleash, GrowthBook), env vars named *_ENABLED / FEATURE_*, or config. Say "None found" if none. -->

| Flag | Default | Effect | Defined in |
|---|---|---|---|
| `{{flag}}` | {{default}} | {{effect}} | `{{file}}` |

## Per-environment differences

| Variable | Development | Staging | Production |
|---|---|---|---|
| `{{NAME}}` | {{value class}} | | |

## Related documents

[Developer Guide](dev-guide.md) · [Third-Party Services Inventory](third-party-services.md)

## Assumptions and open questions

| # | Item | Type | Why unverified | Who can confirm |
|---|------|------|----------------|-----------------|
| A1 | {{item}} | assumption | {{reason}} | {{role}} |
