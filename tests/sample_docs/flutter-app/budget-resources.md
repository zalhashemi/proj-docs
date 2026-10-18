---
title: Budget and Resource Plan
subtitle: "Trailmate"
version: 1.0.0
date: "2026-10-18"
author: "Trailmate team"
project: "Trailmate"
doc_id: budget-resources
confidential: true
---

*Planning estimates only, not financial advice.*

> [!NOTE]
> These figures use **sample inputs** supplied to demonstrate the skill. They are not real Trailmate data.

One developer builds and ships the app to both stores in 2027.


## Inputs

Currency: **USD**. Period: **12 months from 2027-01**, contingency **15%**.

| Input | Value | Source | Assumption |
|---|---|---|---|
| `currency` | USD | user | — |
| `budget_start` | 2027-01 | user | — |
| `contingency_pct` | 15 | default | ⟨assumption⟩ |
| `team_roles` | 1 item(s) | user | — |
| `tooling_costs` | 1 item(s) | user | — |
| `fixed_infra_cost` | 25 | user | — |
| `one_time_costs` | 2 item(s) | user | — |

## Team

| Role | Allocation | Monthly rate | Monthly cost | Annual cost |
|---|---:|---:|---:|---:|
| Flutter developer | 100% | USD 7,000 | USD 7,000 | USD 84,000 |

## Infrastructure and tooling

| Item | Monthly | Annual |
|---|---:|---:|
| Firebase Blaze (base) | USD 25 | USD 300 |
| Infrastructure (fixed) | USD 25 | USD 300 |

## Licences and one-time costs

| Item | Amount | Quarter |
|---|---:|---|
| Apple Developer Program | USD 99 | Q1 ⟨assumption⟩ |
| Google Play registration | USD 25 | Q1 ⟨assumption⟩ |

## Totals by quarter

![Budget by quarter (USD)](.project-docs/assets/budget-quarters.png)

| Quarter | Recurring | One-time | Contingency | Total |
|---|---:|---:|---:|---:|
| Q1 (Jan 2027 – Mar 2027) | USD 21,150 | USD 124 | USD 3,191 | USD 24,465 |
| Q2 (Apr 2027 – Jun 2027) | USD 21,150 | USD 0 | USD 3,172 | USD 24,322 |
| Q3 (Jul 2027 – Sep 2027) | USD 21,150 | USD 0 | USD 3,172 | USD 24,322 |
| Q4 (Oct 2027 – Dec 2027) | USD 21,150 | USD 0 | USD 3,172 | USD 24,322 |
| **Year** | **USD 84,600** | **USD 124** | **USD 12,709** | **USD 97,433** |

## Formulas

```text
team_monthly[r]   = allocation[r] × monthly_rate[r]
recurring_monthly = Σ team_monthly + Σ tooling + fixed_infra
recurring[q]      = 3 × recurring_monthly
contingency[q]    = (recurring[q] + one_time[q]) × contingency_pct
total[q]          = recurring[q] + one_time[q] + contingency[q]
```

One-time costs without a month are placed in Q1 ⟨assumption⟩.


## Related documents

[1-Year Forecast](forecast-1yr.md)

## Assumptions and open questions

| # | Item | Type | Why unverified | Who can confirm |
|---|------|------|----------------|-----------------|
| A1 | Contingency % not provided; default 15% used | assumption | answered "unknown" | product owner |
| A2 | Store fees land in Q1 | assumption | no month given | product owner |
