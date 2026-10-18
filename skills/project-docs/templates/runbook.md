---
title: Runbook
subtitle: "{{project_name}}"
version: 1.0.0
date: "{{YYYY-MM-DD}}"
author: "{{author}}"
project: "{{project_name}}"
doc_id: runbook
confidential: false
---

<!-- guide: For an operator at 3 a.m. Short imperative steps, exact commands, expected output.
Commands come from scripts, compose, k8s manifests, Procfile. Mark platform commands you can't
verify from the repo ⟨untested⟩. -->

## Service overview

| | |
|---|---|
| Hosting | {{hosting}} |
| Components | {{list}} |
| Health endpoint | `{{/health}}` (`{{file}}`) |
| On-call | {{oncall_contact}} |
| Dashboards | {{links ⟨assumption⟩}} |

## Start, stop, restart

```bash
{{start}}
{{stop}}
{{restart}}
```

## Health checks

```bash
curl -fsS {{base_url}}/{{health}}
```

Expected: `{{response}}`

## Routine tasks

<!-- guide: Migrations, cache clear, log rotation, certificate renewal, scheduled jobs (cron, queues), backups. -->

| Task | Frequency | Command |
|---|---|---|
| {{task}} | {{frequency}} | `{{command}}` |

## Logs

{{where logs go and how to read/tail them}}

```bash
{{log command}}
```

## Common problems

<!-- guide: Symptom → check → fix. 4–8 entries grounded in the code (DB connection errors, missing env var, port in use, queue backlog). -->

### {{Symptom}}

1. Check: `{{command}}`
2. Fix: {{fix}}

## Scaling

{{how to scale: replicas, instance size, worker counts, from infra config}}

## Escalation

See [Incident Response](incident-response.md).

## Related documents

[Incident Response](incident-response.md) · [Monitoring and SLOs](monitoring-slos.md) · [Troubleshooting and FAQ](troubleshooting-faq.md)

## Assumptions and open questions

| # | Item | Type | Why unverified | Who can confirm |
|---|------|------|----------------|-----------------|
| A1 | {{item}} | assumption | {{reason}} | {{role}} |
