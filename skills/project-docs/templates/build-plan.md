---
title: Build Plan
subtitle: "{{project_name}}"
version: 1.0.0
date: "{{YYYY-MM-DD}}"
author: "{{author}}"
project: "{{project_name}}"
doc_id: build-plan
confidential: false
---

<!-- guide: The only doc made before the project is built. It records intent, not facts about
code. Everything here is a plan, so label guesses ⟨assumption⟩ freely, but never present a
plan item as already done. Keep it to 3–5 pages. -->

## Summary

<!-- guide: 3–4 sentences: what will be built, for whom, by when, by how many people.
Source: inputs.project_goal, target_users, deadline, team_size. -->

{{project_goal}}

| Item | Plan |
|---|---|
| Target users | {{target_users}} |
| Target date | {{deadline}} |
| Team size | {{team_size}} |
| Current state | {{e.g. empty repo / prototype / spec only}} |

## Goals and non-goals

<!-- guide: 3–5 measurable goals; 2–4 explicit non-goals to prevent scope creep. -->

**Goals**

1. {{goal}}

**Non-goals**

- {{non_goal}}

## Scope: first release

<!-- guide: Bullet the minimum feature set that makes the project useful. Anything else
goes under "Later". This is the smallest version that does the core job. -->

| Feature | Why it's needed | Priority (Must/Should/Could) |
|---|---|---|
| {{feature}} | {{reason}} | Must |

**Later:** {{deferred features}}

## Proposed stack

<!-- guide: If the repo already has manifests, use what's there and cite them. Otherwise
propose the simplest stack that fits inputs.stack_preference and justify each choice in one line. -->

| Layer | Choice | Reason |
|---|---|---|
| Frontend | {{choice}} | {{reason}} |
| Backend | {{choice}} | {{reason}} |
| Data | {{choice}} | {{reason}} |
| Hosting | {{choice}} | {{reason}} |

## Phases and milestones

<!-- guide: 3–6 phases, each with a clear exit check ("done when …"). Dates are targets,
mark them ⟨assumption⟩ unless the user gave them. -->

| Phase | Deliverables | Done when | Target date |
|---|---|---|---|
| 1. Foundation | {{deliverables}} | {{exit check}} | {{date}} ⟨assumption⟩ |

## Risks

<!-- guide: Top 5 risks only. Full register comes later (risk-register) once the project exists. -->

| Risk | Likelihood (L/M/H) | Impact (L/M/H) | Mitigation |
|---|---|---|---|
| {{risk}} | M | H | {{mitigation}} |

## Documentation plan

<!-- guide: Explain that the full docs pack (dev guide, architecture, runbook, …) will be
generated once the project is complete, and list which packs are likely to be wanted. -->

The full documentation set is generated when the project is complete. Packs likely to be needed: {{packs}}.

## Open decisions

- {{decision needed, owner, by when}}

## Assumptions and open questions

<!-- guide: Repeat every ⟨assumption⟩ and [!ASSUMPTION] from this doc, one row each, plus open questions. -->

| # | Item | Type | Why unverified | Who can confirm |
|---|------|------|----------------|-----------------|
| A1 | {{item}} | assumption | {{reason}} | {{role}} |
