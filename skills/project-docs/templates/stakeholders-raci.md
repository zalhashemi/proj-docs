---
title: Stakeholders and RACI
subtitle: "{{project_name}}"
version: 1.0.0
date: "{{YYYY-MM-DD}}"
author: "{{author}}"
project: "{{project_name}}"
doc_id: stakeholders-raci
confidential: false
---

<!-- guide: People come ONLY from inputs.stakeholders, CODEOWNERS, or git contributors. Never
invent names. If only git authors are known, list them by role ("maintainer of src/api")
and ask whether to include names. -->

## Stakeholders

| Stakeholder | Role | Interest | Influence (L/M/H) | Source |
|---|---|---|---|---|
| {{name or role}} | {{role}} | {{interest}} | M | {{inputs / CODEOWNERS / git}} |

## Code ownership

<!-- guide: From CODEOWNERS, or the top contributors per top-level directory from git. -->

| Area | Owner(s) | Evidence |
|---|---|---|
| `{{path}}` | {{owner}} | {{CODEOWNERS line / git shortlog}} |

## RACI matrix

**R** = Responsible · **A** = Accountable · **C** = Consulted · **I** = Informed

<!-- guide: 5–10 key activities. Max 5 stakeholder columns to keep it readable on A4. -->

| Activity | {{S1}} | {{S2}} | {{S3}} | {{S4}} |
|---|---|---|---|---|
| Release approval | A | R | C | I |
| Production incidents | | | | |
| Security review | | | | |
| Roadmap decisions | | | | |

## Communication plan

| Audience | What | Channel | Frequency |
|---|---|---|---|
| {{audience}} | {{update type}} | {{channel}} | {{frequency}} |

## Related documents

[Handover](handover.md)

## Assumptions and open questions

| # | Item | Type | Why unverified | Who can confirm |
|---|------|------|----------------|-----------------|
| A1 | {{item}} | assumption | {{reason}} | {{role}} |
