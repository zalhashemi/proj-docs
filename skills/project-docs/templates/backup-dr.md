---
title: Backup and Disaster Recovery
subtitle: "{{project_name}}"
version: 1.0.0
date: "{{YYYY-MM-DD}}"
author: "{{author}}"
project: "{{project_name}}"
doc_id: backup-dr
confidential: false
---

<!-- guide: Only claim backups exist if config shows them (Terraform backup_retention, k8s
CronJob, backup scripts, managed DB settings). Otherwise state "No backup configuration
found in the repo" in a WARNING callout and give a recommended plan marked ⟨assumption⟩. -->

## Data stores

| Store | Contents | Criticality | Backup configured | Evidence |
|---|---|---|---|---|
| {{Postgres}} | {{contents}} | High | {{yes/no}} | `{{path}}` |

## Objectives

| Objective | Target |
|---|---|
| RPO (max data loss) | {{rpo_rto}} |
| RTO (max downtime) | {{rpo_rto}} |

## Backup schedule

| Store | Method | Frequency | Retention | Location |
|---|---|---|---|---|
| {{store}} | {{pg_dump / snapshot}} | {{daily}} | {{30 days}} | {{bucket/region}} |

## Restore procedure

1. {{step}}

   ```bash
   {{restore command}}  ⟨untested⟩
   ```

2. Verify: {{checks}}

## Disaster scenarios

| Scenario | Impact | Recovery steps | Expected RTO |
|---|---|---|---|
| Database corruption | {{impact}} | {{steps}} | {{time}} |
| Region outage | | | |
| Accidental deletion | | | |

## Testing

Run restore drills {{quarterly ⟨assumption⟩}} and record the results here.

## Related documents

[Runbook](runbook.md) · [Data Model](data-model.md)

## Assumptions and open questions

| # | Item | Type | Why unverified | Who can confirm |
|---|------|------|----------------|-----------------|
| A1 | {{item}} | assumption | {{reason}} | {{role}} |
