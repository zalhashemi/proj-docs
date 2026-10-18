---
title: Project Brief
subtitle: "{{project_name}}"
version: 1.0.0
date: "{{YYYY-MM-DD}}"
author: "{{author}}"
project: "{{project_name}}"
doc_id: project-brief
confidential: false
---

<!-- guide: One page (two at most). Lead with the problem and the status. No feature lists
longer than 5 bullets. Readers are execs and new stakeholders. -->

## At a glance

| | |
|---|---|
| What | {{one-line description, from README or package description}} |
| For whom | {{target_users}} |
| Status | {{e.g. "In production since 2025-03 (first tag v1.0.0)", from git}} |
| Stack | {{frameworks from scan}} |
| Team | {{contributor count from git, or inputs}} |

## Problem

<!-- guide: 2–3 sentences. Source: inputs.project_goal, README intro. -->

{{problem}}

## Solution

<!-- guide: What the project does, in plain language. Mention project type (web app, API, CLI…). -->

{{solution}}

## Key capabilities

<!-- guide: 3–5 bullets, each traceable to routes, pages, commands or modules. -->

- {{capability}} (`{{evidence path}}`)

## Current status and next steps

<!-- guide: Recent activity from git (last commit date, commits in last 90 days), latest
release, and up to 3 next steps (from roadmap inputs or open TODOs). -->

- Latest release: {{tag/date}}
- Recent activity: {{commits / period}}
- Next: {{next steps}}

## Related documents

[PRD](prd.md) · [Roadmap](roadmap.md)

## Assumptions and open questions

| # | Item | Type | Why unverified | Who can confirm |
|---|------|------|----------------|-----------------|
| A1 | {{item}} | assumption | {{reason}} | {{role}} |
