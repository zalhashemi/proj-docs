---
title: Admin Guide
subtitle: "{{project_name}}"
version: 1.0.0
date: "{{YYYY-MM-DD}}"
author: "{{author}}"
project: "{{project_name}}"
doc_id: admin-guide
confidential: false
---

<!-- guide: For people who administer the system (not developers). Derive roles/permissions
from code (role enums, permission checks, admin routes, Django admin). If there is no admin
concept, describe operator-level settings via config instead and say so. -->

## Roles and permissions

| Role | Can | Cannot | Defined in |
|---|---|---|---|
| {{admin}} | {{permissions}} | {{limits}} | `{{path}}` |

## Managing users

### {{Invite / create a user}}

1. {{step}}

### {{Change a role / deactivate a user}}

1. {{step}}

## System settings

| Setting | Where | Effect |
|---|---|---|
| {{setting}} | {{admin UI / env var}} | {{effect}} |

## Maintenance tasks

| Task | How | Frequency |
|---|---|---|
| {{task}} | {{steps/command}} | {{frequency}} |

## Audit and logs

{{where admin actions are logged, if they are}}

## Related documents

[User Guide](user-guide.md) · [Environment and Configuration Reference](env-config-reference.md)

## Assumptions and open questions

| # | Item | Type | Why unverified | Who can confirm |
|---|------|------|----------------|-----------------|
| A1 | {{item}} | assumption | {{reason}} | {{role}} |
