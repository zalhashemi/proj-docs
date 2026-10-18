---
title: Upgrade and Migration Guide
subtitle: "{{project_name}}"
version: 1.0.0
date: "{{YYYY-MM-DD}}"
author: "{{author}}"
project: "{{project_name}}"
doc_id: upgrade-migration-guide
confidential: false
---

<!-- guide: Breaking changes come from CHANGELOG "BREAKING" entries, conventional-commit "!"
markers, major-version tags, removed/renamed routes, env vars and DB migrations between
from_version and HEAD. List only changes you can evidence. -->

## Versions covered

From **{{from_version}}** to **{{to_version}}** ({{date range}}).

## Breaking changes

| Change | Who is affected | Action required | Evidence |
|---|---|---|---|
| {{change}} | {{API clients / operators / users}} | {{action}} | `{{commit/changelog}}` |

## Upgrade steps

<!-- guide: Ordered and copy-pasteable: back up, update code/image, update config, run migrations, verify. -->

1. Back up data. See [Backup and Disaster Recovery](backup-dr.md).
2. {{update command}}
3. Update configuration:

   | Variable | Change |
   |---|---|
   | `{{NAME}}` | {{added/renamed/removed}} |

4. Run migrations:

   ```bash
   {{migrate command}}
   ```

5. Verify: {{health check}}

## Database migrations in this range

| Migration | What it does | Reversible |
|---|---|---|
| `{{name}}` | {{effect}} | {{yes/no}} |

## Rollback

{{how to roll back, and any point of no return (irreversible migrations)}}

## Related documents

[Release Notes](release-notes.md)

## Assumptions and open questions

| # | Item | Type | Why unverified | Who can confirm |
|---|------|------|----------------|-----------------|
| A1 | {{item}} | assumption | {{reason}} | {{role}} |
