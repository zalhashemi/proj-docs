---
title: Support and SLA
subtitle: "{{project_name}}"
version: 1.0.0
date: "{{YYYY-MM-DD}}"
author: "{{author}}"
project: "{{project_name}}"
doc_id: support-sla
confidential: false
---

*Template for discussion with qualified counsel. Not legal advice.*

<!-- guide: Commitments come only from inputs. Anything the user didn't provide is a proposed
default marked ⟨assumption⟩, clearly a draft. Availability target must match monitoring-slos. -->

## Scope

{{which product, environments and customers this covers}}

## Support channels and hours

| Channel | Hours | Languages |
|---|---|---|
| {{support_channels}} | {{support_hours}} | {{languages}} |

## Priority definitions

| Priority | Definition | First response | Target resolution |
|---|---|---|---|
| P1 Critical | Service unavailable | {{1 h ⟨assumption⟩}} | {{4 h}} |
| P2 High | Major feature impaired | {{4 h}} | {{1 business day}} |
| P3 Normal | Minor issue or question | {{1 business day}} | {{5 business days}} |
| P4 Low | Feature request | {{3 business days}} | best effort |

## Availability commitment

| Metric | Target | Measurement window | Exclusions |
|---|---|---|---|
| Uptime | {{slo_targets}} | Calendar month | Scheduled maintenance ({{notice period}}) |

## Service credits

{{credit schedule, or "None offered" ⟨assumption⟩}}

## Escalation

1. {{level 1}}
2. {{level 2}}

## Customer responsibilities

- {{e.g. provide reproduction steps, keep contacts current}}

## Related documents

[Incident Response](incident-response.md) · [Monitoring and SLOs](monitoring-slos.md)

## Assumptions and open questions

| # | Item | Type | Why unverified | Who can confirm |
|---|------|------|----------------|-----------------|
| A1 | {{item}} | assumption | {{reason}} | {{role}} |
