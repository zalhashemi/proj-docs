---
title: Third-Party Services Inventory
subtitle: "{{project_name}}"
version: 1.0.0
date: "{{YYYY-MM-DD}}"
author: "{{author}}"
project: "{{project_name}}"
doc_id: third-party-services
confidential: true
---

<!-- guide: Services come from scan.third_party (SDK imports, API hostnames, env var prefixes
like STRIPE_, SENDGRID_, AWS_). Plans, costs and account owners are NOT in the repo; they come
from inputs or are ⟨assumption⟩. Env vars: names only. -->

## Summary

{{n}} external services were found. {{n}} of them are critical: the product stops working without them.

## Services

| Service | Purpose | Env vars | Critical | Evidence |
|---|---|---|---|---|
| {{Stripe}} | {{payments}} | `{{STRIPE_SECRET_KEY}}` | {{yes/no}} | `{{path}}` |

## Accounts and costs

| Service | Account owner | Plan | Monthly cost | Renewal |
|---|---|---|---|---|
| {{service}} | {{service_owners}} | {{plan}} ⟨assumption⟩ | {{cost}} ⟨assumption⟩ | {{date}} |

## Failure impact

<!-- guide: What the user sees if each critical service is down, and whether code has a fallback (retry, queue, feature degrade). -->

| Service | If unavailable | Fallback in code | Evidence |
|---|---|---|---|
| {{service}} | {{impact}} | {{yes/no}} | `{{path}}` |

## Handover checklist

- [ ] Transfer account ownership or admin access for each service
- [ ] Rotate API keys after the handover
- [ ] Update billing contacts

## Related documents

[Environment and Configuration Reference](env-config-reference.md) · [Budget and Resource Plan](budget-resources.md)

## Assumptions and open questions

| # | Item | Type | Why unverified | Who can confirm |
|---|------|------|----------------|-----------------|
| A1 | {{item}} | assumption | {{reason}} | {{role}} |
