---
title: Risk Register
subtitle: "{{project_name}}"
version: 1.0.0
date: "{{YYYY-MM-DD}}"
author: "{{author}}"
project: "{{project_name}}"
doc_id: risk-register
confidential: false
---

<!-- guide: Combine user-known risks (inputs.known_risks) with risks evidenced in the repo:
outdated/unmaintained deps, no tests in a critical area, single contributor (bus factor),
no CI, secrets in config, no backups configured. Cite evidence for each repo-derived risk. -->

## Scoring

Likelihood and impact are each rated 1 (low) to 5 (high). **Score = likelihood × impact.**
A score of 15+ is high, 8–14 is medium, and 7 or below is low.

## Register

<!-- guide: Sort by score descending. Keep text short so the table fits; put detail below if needed.
Owner: use inputs.risk_owners; otherwise "unassigned ⟨assumption⟩". -->

| ID | Risk | L | I | Score | Owner | Mitigation | Trigger |
|---|---|---|---|---|---|---|---|
| R1 | {{risk}} | 3 | 4 | 12 | {{owner}} | {{mitigation}} | {{early warning sign}} |

## Evidence

<!-- guide: One line per repo-derived risk: ID → file/command that shows it. -->

- R1: `{{path or command}}`

## Review cadence

Review this register {{monthly ⟨assumption⟩}} and whenever a trigger fires.

## Related documents

[Roadmap](roadmap.md) · [Security Threat Model](security-threat-model.md) · [Tech Debt Register](tech-debt-register.md)

## Assumptions and open questions

| # | Item | Type | Why unverified | Who can confirm |
|---|------|------|----------------|-----------------|
| A1 | {{item}} | assumption | {{reason}} | {{role}} |
