---
title: Compliance Checklist
subtitle: "{{project_name}}"
version: 1.0.0
date: "{{YYYY-MM-DD}}"
author: "{{author}}"
project: "{{project_name}}"
doc_id: compliance-checklist
confidential: true
---

*Template for discussion with qualified counsel. Not legal advice.*

<!-- guide: Include only the frameworks in inputs.compliance_frameworks; delete the other sections.
Status values: "evidence found" (cite path), "not found", "needs review". NEVER write
"compliant". Many controls are organisational and not visible in code, so mark them needs review. -->

**Status key:** evidence found · not found · needs review

## GDPR

| Control | Status | Evidence / notes |
|---|---|---|
| Lawful basis documented for each processing purpose | needs review | |
| Privacy notice available to users | {{status}} | `{{path}}` |
| Data subject access / export | {{status}} | |
| Right to erasure implemented | {{status}} | |
| Data retention limits enforced | {{status}} | |
| Records of processing activities | needs review | |
| DPA with each subprocessor | needs review | See [Third-Party Services](third-party-services.md) |
| Breach notification process (72 h) | {{status}} | See [Incident Response](incident-response.md) |
| Encryption in transit | {{status}} | |
| Cross-border transfer safeguards | needs review | |

## SOC 2 (Trust Services Criteria)

| Criterion | Control | Status | Evidence / notes |
|---|---|---|---|
| CC6 Logical access | Authentication and role-based access | {{status}} | |
| CC6 Logical access | MFA for admin / infra access | needs review | |
| CC7 System operations | Monitoring and alerting | {{status}} | |
| CC7 System operations | Incident response process | {{status}} | |
| CC8 Change management | Code review required (PRs) | {{status}} | |
| CC8 Change management | CI tests before deploy | {{status}} | |
| A1 Availability | Backups and restore tested | {{status}} | |
| C1 Confidentiality | Secrets not in source control | {{status}} | |
| CC9 Risk mitigation | Vendor risk management | needs review | |

## HIPAA (Security Rule)

| Safeguard | Control | Status | Evidence / notes |
|---|---|---|---|
| Technical | Unique user identification | {{status}} | |
| Technical | Audit controls / logging of PHI access | {{status}} | |
| Technical | Encryption of PHI at rest and in transit | {{status}} | |
| Technical | Automatic logoff | {{status}} | |
| Administrative | Risk analysis performed | needs review | |
| Administrative | BAAs with vendors handling PHI | needs review | |
| Physical | Hosting provider safeguards | needs review | |

## Summary of gaps

| Gap | Framework | Suggested action | Priority |
|---|---|---|---|
| {{gap}} | {{framework}} | {{action}} | {{H/M/L}} |

## Related documents

[Privacy and Data Handling](privacy-data-handling.md) · [Security Threat Model](security-threat-model.md)

## Assumptions and open questions

| # | Item | Type | Why unverified | Who can confirm |
|---|------|------|----------------|-----------------|
| A1 | {{item}} | assumption | {{reason}} | {{role}} |
