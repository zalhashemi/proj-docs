---
title: Monitoring and SLOs
subtitle: "{{project_name}}"
version: 1.0.0
date: "{{YYYY-MM-DD}}"
author: "{{author}}"
project: "{{project_name}}"
doc_id: monitoring-slos
confidential: false
---

<!-- guide: Current instrumentation from code (Sentry/Datadog/OTel SDKs, Prometheus metrics,
health endpoints, structured logging). Targets from inputs.slo_targets; proposed SLOs without
user input are ⟨assumption⟩. -->

## Current instrumentation

| Signal | Tool | Evidence |
|---|---|---|
| Errors | {{Sentry / none}} | `{{path}}` |
| Metrics | {{Prometheus / none}} | `{{path}}` |
| Traces | {{OTel / none}} | `{{path}}` |
| Logs | {{logger}} | `{{path}}` |
| Health | `{{/health}}` | `{{path}}` |

## Service level indicators

| SLI | Definition | Measured by |
|---|---|---|
| Availability | Successful requests ÷ total requests | {{source}} |
| Latency | p95 response time for `{{key endpoints}}` | {{source}} |

## Service level objectives

| SLO | Target | Window | Error budget |
|---|---|---|---|
| Availability | {{99.9% ⟨assumption⟩}} | 30 days | {{43 min}} |
| Latency p95 | {{< 300 ms ⟨assumption⟩}} | 30 days | |

## Alerts

| Alert | Condition | Severity | Action |
|---|---|---|---|
| {{alert}} | {{condition}} | {{SEV}} | [Runbook](runbook.md) § {{section}} |

## Dashboards

- {{dashboard ⟨assumption⟩}}

## Gaps

- {{e.g. "No metrics endpoint; add Prometheus client"}}

## Related documents

[Runbook](runbook.md) · [Support and SLA](support-sla.md)

## Assumptions and open questions

| # | Item | Type | Why unverified | Who can confirm |
|---|------|------|----------------|-----------------|
| A1 | {{item}} | assumption | {{reason}} | {{role}} |
