---
title: Privacy and Data Handling
subtitle: "{{project_name}}"
version: 1.0.0
date: "{{YYYY-MM-DD}}"
author: "{{author}}"
project: "{{project_name}}"
doc_id: privacy-data-handling
confidential: true
---

*Template for discussion with qualified counsel. Not legal advice.*

<!-- guide: Data inventory from the data model (fields that look like personal data: email,
name, phone, address, ip, dob, payment). Subprocessors from third_party. Legal bases,
retention and regions come from inputs or are open questions. Never assert compliance. -->

## Personal data inventory

| Data category | Fields | Stored in | Purpose | Evidence |
|---|---|---|---|---|
| {{Contact}} | `{{email, name}}` | {{table}} | {{purpose}} | `{{path}}` |

## Data flows

```mermaid
flowchart LR
  user([Data subject]) --> app[{{project_name}}] --> db[(Storage)]
  app --> sp[(Subprocessor)]
```

## Subprocessors

| Service | Data shared | Purpose | Region |
|---|---|---|---|
| {{service}} | {{data}} | {{purpose}} | {{region ⟨assumption⟩}} |

## Retention

| Data | Retention period | Deletion mechanism | Evidence |
|---|---|---|---|
| {{data}} | {{retention_policy}} | {{job / manual / none found}} | `{{path}}` |

## Data subject rights

| Right | Supported | How | Evidence |
|---|---|---|---|
| Access / export | {{evidence found / not found}} | {{how}} | `{{path}}` |
| Deletion | | | |
| Rectification | | | |

## Security measures

{{encryption in transit/at rest, access control, from config. Link to the Security Threat Model.}}

## Open questions for counsel

- {{question}}

## Related documents

[Data Model](data-model.md) · [Third-Party Services Inventory](third-party-services.md) · [Compliance Checklist](compliance-checklist.md)

## Assumptions and open questions

| # | Item | Type | Why unverified | Who can confirm |
|---|------|------|----------------|-----------------|
| A1 | {{item}} | assumption | {{reason}} | {{role}} |
