---
title: Incident Response
subtitle: "{{project_name}}"
version: 1.0.0
date: "{{YYYY-MM-DD}}"
author: "{{author}}"
project: "{{project_name}}"
doc_id: incident-response
confidential: false
---

<!-- guide: Process doc. People/channels only from inputs; otherwise use role names and mark
⟨assumption⟩. Keep severity definitions concrete for this system (e.g. "checkout API down"). -->

## Severity levels

| Severity | Definition | Example for this system | Response time |
|---|---|---|---|
| SEV1 | Full outage or data loss | {{example}} | {{15 min ⟨assumption⟩}} |
| SEV2 | Major feature degraded | {{example}} | {{1 h}} |
| SEV3 | Minor issue, workaround exists | {{example}} | {{next business day}} |

## Roles

| Role | Responsibility | Who |
|---|---|---|
| Incident commander | Coordinates, decides | {{oncall_contact}} |
| Communications | Updates stakeholders | {{who}} |
| Responder | Investigates and fixes | {{who}} |

## Response steps

1. **Detect:** alert, user report or monitoring. See [Monitoring and SLOs](monitoring-slos.md).
2. **Declare:** set the severity and open a channel or ticket in {{status_page}}.
3. **Mitigate:** stabilise first, using rollback ([CI/CD](cicd-deployment.md)) or the [Runbook](runbook.md).
4. **Communicate:** send updates every {{30 min ⟨assumption⟩}} for SEV1 and SEV2.
5. **Resolve:** confirm recovery with health checks.
6. **Review:** write a postmortem within {{5 business days}}.

## Communication templates

```text
[{{SEV}}] {{project_name}}: {{short description}}
Impact: {{who/what is affected}}
Status: Investigating | Mitigated | Resolved
Next update: {{time}}
```

## Escalation path

{{escalation chain}}

## Postmortem template

<div class="page-break"></div>

### Postmortem: {{incident title}}

| | |
|---|---|
| Date | |
| Severity | |
| Duration | |
| Authors | |

**Summary:** what happened, in two sentences.

**Impact:** users affected, duration, data affected.

**Timeline** (UTC)

| Time | Event |
|---|---|
| | |

**Root cause:**

**What went well / what didn't:**

**Action items**

| Action | Owner | Due | Ticket |
|---|---|---|---|
| | | | |

*Blameless: focus on systems and processes, not individuals.*

## Related documents

[Runbook](runbook.md) · [Monitoring and SLOs](monitoring-slos.md)

## Assumptions and open questions

| # | Item | Type | Why unverified | Who can confirm |
|---|------|------|----------------|-----------------|
| A1 | {{item}} | assumption | {{reason}} | {{role}} |
