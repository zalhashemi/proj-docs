---
title: Product Requirements Document
subtitle: "{{project_name}}"
version: 1.0.0
date: "{{YYYY-MM-DD}}"
author: "{{author}}"
project: "{{project_name}}"
doc_id: prd
confidential: false
---

<!-- guide: Describe the product as it exists (from routes, pages, commands) plus what the
user says it should become. Clearly separate "Implemented" from "Planned" so readers
never mistake a wish for a shipped feature. -->

## Overview

{{2–3 sentence product summary}}

## Goals

<!-- guide: Measurable. Source: inputs.success_metrics. If unknown, write the goal and mark the metric ⟨assumption⟩. -->

| Goal | Metric | Target |
|---|---|---|
| {{goal}} | {{metric}} | {{target}} |

## Non-goals

- {{non_goal}}

## Personas

<!-- guide: 2–4 personas from inputs.target_users and role names found in code (admin, user, guest). -->

| Persona | Needs | Evidence |
|---|---|---|
| {{persona}} | {{needs}} | {{e.g. role enum in src/models/user.ts}} |

## User stories

<!-- guide: "As a <persona>, I want <capability> so that <outcome>." Group by area. Tag each
Implemented (cite route/page) or Planned. -->

| ID | Story | Status | Evidence |
|---|---|---|---|
| US-1 | As a {{persona}}, I want {{capability}} so that {{outcome}}. | Implemented | `{{path}}` |

## Requirements

### Functional

<!-- guide: MoSCoW priority. Must = required for release. -->

| ID | Requirement | Priority | Story |
|---|---|---|---|
| FR-1 | {{requirement}} | Must | US-1 |

### Non-functional

| ID | Requirement | Target | Evidence |
|---|---|---|---|
| NFR-1 | Performance: {{e.g. p95 latency}} | {{target}} ⟨assumption⟩ | {{none / config}} |

## Acceptance criteria

<!-- guide: Given/When/Then per Must requirement. Point to existing tests where they cover it. -->

**FR-1**
- Given {{context}}, when {{action}}, then {{result}}. Test: `{{test path or "none"}}`

## Open questions

- {{question}}

## Related documents

[Project Brief](project-brief.md) · [Roadmap](roadmap.md)

## Assumptions and open questions

| # | Item | Type | Why unverified | Who can confirm |
|---|------|------|----------------|-----------------|
| A1 | {{item}} | assumption | {{reason}} | {{role}} |
