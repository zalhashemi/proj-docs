---
title: Competitive Analysis
subtitle: "{{project_name}}"
version: 1.0.0
date: "{{YYYY-MM-DD}}"
author: "{{author}}"
project: "{{project_name}}"
doc_id: competitive-analysis
confidential: true
---

<!-- guide: Competitor facts are NOT in the repo. Only use competitors the user named
(inputs.competitors) and only claims the user provided or that are general public knowledge
you are confident in; mark everything else ⟨assumption⟩ and recommend verification. Our own
capabilities must come from the repo. -->

## Summary

{{2–3 sentences: market position and main differentiator}}

## Alternatives considered

| Alternative | Type | Target users | Pricing model |
|---|---|---|---|
| {{competitor}} | {{SaaS / OSS / in-house}} | {{users}} | {{pricing}} ⟨assumption⟩ |

## Feature comparison

<!-- guide: ✓ = has, ✗ = lacks, ~ = partial, ? = unknown. Max 5 product columns. -->

| Capability | {{project_name}} | {{C1}} | {{C2}} | {{C3}} |
|---|---|---|---|---|
| {{capability}} | ✓ | ? | ? | ? |

## Positioning

<!-- guide: Where this project wins and where it loses. Be honest about the gaps. -->

- **Strengths:** {{strengths}}
- **Gaps:** {{gaps}}

## Differentiation

{{inputs.differentiators, grounded in what the code actually does}}

## Recommendations

- {{recommendation}}

## Related documents

[PRD](prd.md)

## Assumptions and open questions

| # | Item | Type | Why unverified | Who can confirm |
|---|------|------|----------------|-----------------|
| A1 | {{item}} | assumption | {{reason}} | {{role}} |
