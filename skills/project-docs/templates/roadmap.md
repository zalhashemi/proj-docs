---
title: Roadmap
subtitle: "{{project_name}}"
version: 1.0.0
date: "{{YYYY-MM-DD}}"
author: "{{author}}"
project: "{{project_name}}"
doc_id: roadmap
confidential: false
---

<!-- guide: Past = facts from git tags/CHANGELOG. Future = plan from inputs; every future date
is a target, so mark user-unconfirmed ones ⟨assumption⟩. Horizon: inputs.roadmap_horizon_months. -->

## Where we are

<!-- guide: Last 2–3 releases with dates from git tags or CHANGELOG. -->

| Release | Date | Highlights |
|---|---|---|
| {{tag}} | {{date}} | {{summary}} |

## Phases

| Phase | Goal | Milestones | Depends on |
|---|---|---|---|
| {{phase}} | {{goal}} | {{M1, M2}} | {{dependency}} |

## Milestones

| ID | Milestone | Target | Owner | Status |
|---|---|---|---|---|
| M1 | {{milestone}} | {{YYYY-MM}} | {{owner}} | Planned |

## Timeline

<!-- guide: Gantt-style table. One row per milestone or workstream, one column per month
(max 12; use quarters if longer). Fill active cells with ■ and leave others empty. Keep the
first column short so the table fits A4. -->

<div class="gantt">

| Workstream | {{M1}} | {{M2}} | {{M3}} | {{M4}} | {{M5}} | {{M6}} | {{M7}} | {{M8}} | {{M9}} | {{M10}} | {{M11}} | {{M12}} |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| {{workstream}} | ■ | ■ | | | | | | | | | | |

</div>

## Dependencies and risks

<!-- guide: External or cross-team dependencies that could move dates. Link the risk register. -->

- {{dependency}}: affects {{milestone}}

See [Risk Register](risk-register.md).

## Related documents

[PRD](prd.md) · [Risk Register](risk-register.md)

## Assumptions and open questions

| # | Item | Type | Why unverified | Who can confirm |
|---|------|------|----------------|-----------------|
| A1 | {{item}} | assumption | {{reason}} | {{role}} |
