---
title: Handover Document
subtitle: "{{project_name}}"
version: 1.0.0
date: "{{YYYY-MM-DD}}"
author: "{{author}}"
project: "{{project_name}}"
doc_id: handover
confidential: true
---

<!-- guide: The single entry point for a new team. Summarise and point to the Developer and Ops
packs by name rather than repeating them. The repo can't show access, people or tribal knowledge, so those
come from inputs or appear as open questions. -->

## Handover summary

| | |
|---|---|
| From | {{handover_from}} |
| To | {{handover_to}} |
| Date | {{date}} |
| Repository | {{remote url}} |
| Status | {{production / beta / prototype, with evidence}} |

## System at a glance

{{3–5 sentences: what it does, stack, where it runs. Point to the Developer pack, Architecture chapter.}}

| Area | Summary | Where to read more |
|---|---|---|
| Code and local setup | {{summary}} | Developer pack, Developer Guide |
| Architecture | {{summary}} | Developer pack, Architecture |
| Deployment | {{summary}} | Developer pack, CI/CD and Deployment |
| Operations | {{summary}} | Ops pack, Runbook |
| External services | {{n}} services | Ops pack, Third-Party Services |

## Access to transfer

<!-- guide: inputs.access_list plus everything implied by the repo: git hosting, CI, cloud
accounts (from infra), each third-party service, domains/DNS, app stores (mobile). -->

| System | Access type | Current holder | Transferred |
|---|---|---|---|
| {{system}} | {{admin/owner}} | {{who}} | ☐ |

## Current state

- **Recent work:** {{git log summary, last 3 months}}
- **In progress:** {{open branches / TODOs}}
- **Known issues:** see [Tech Debt Register](tech-debt-register.md)

## Knowledge transfer

<!-- guide: Non-obvious things: gotchas found in comments, unusual config, manual steps in scripts. -->

- {{gotcha}} (`{{path}}`)

## First 30 days for the new team

- [ ] Run the project locally ([Developer Guide](dev-guide.md))
- [ ] Deploy to a non-production environment
- [ ] Rotate credentials after access transfer
- [ ] Review the [Risk Register](risk-register.md) and [Tech Debt Register](tech-debt-register.md)
- [ ] {{item}}

## Contacts

| Topic | Contact | Until |
|---|---|---|
| {{topic}} | {{contact}} | {{date}} |

## Related documents

[Developer Guide](dev-guide.md) · [Architecture](architecture.md) · [Runbook](runbook.md) · [Third-Party Services](third-party-services.md) · [Tech Debt Register](tech-debt-register.md)

## Assumptions and open questions

| # | Item | Type | Why unverified | Who can confirm |
|---|------|------|----------------|-----------------|
| A1 | {{item}} | assumption | {{reason}} | {{role}} |
