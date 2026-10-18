---
title: Budget and Resource Plan
subtitle: "BrightCart"
version: 1.0.0
date: "2026-10-18"
author: "BrightCart team"
project: "BrightCart"
doc_id: budget-resources
confidential: true
---

*Planning estimates only, not financial advice.*

> [!NOTE]
> These figures use **sample inputs** supplied to demonstrate the skill. They are not real BrightCart data.

The plan covers the people and tools needed to run the BrightCart storefront in 2027. Tooling lines match services found in the repo: Vercel (`vercel.json`), Sentry (`@sentry/react`) and GitHub Actions (`.github/workflows/ci.yml`).


## Inputs

Currency: **EUR**. Period: **12 months from 2027-01**, contingency **15%**.

| Input | Value | Source | Assumption |
|---|---|---|---|
| `currency` | EUR | user | — |
| `budget_start` | 2027-01 | user | — |
| `contingency_pct` | 15 | user | — |
| `team_roles` | 3 item(s) | user | — |
| `tooling_costs` | 3 item(s) | user | — |
| `fixed_infra_cost` | 120 | user | — |
| `one_time_costs` | 2 item(s) | user | — |

## Team

| Role | Allocation | Monthly rate | Monthly cost | Annual cost |
|---|---:|---:|---:|---:|
| Frontend developer | 100% | EUR 7,500 | EUR 7,500 | EUR 90,000 |
| Product designer | 40% | EUR 6,500 | EUR 2,600 | EUR 31,200 |
| Product manager | 20% | EUR 9,000 | EUR 1,800 | EUR 21,600 |

## Infrastructure and tooling

| Item | Monthly | Annual |
|---|---:|---:|
| Vercel Pro | EUR 20 | EUR 240 |
| Sentry Team | EUR 26 | EUR 312 |
| GitHub Team | EUR 16 | EUR 192 |
| Infrastructure (fixed) | EUR 120 | EUR 1,440 |

## Licences and one-time costs

| Item | Amount | Quarter |
|---|---:|---|
| Accessibility audit | EUR 4,000 | Q1 |
| Product photography | EUR 2,500 | Q1 ⟨assumption⟩ |

## Totals by quarter

![Budget by quarter (EUR)](.project-docs/assets/budget-quarters.png)

| Quarter | Recurring | One-time | Contingency | Total |
|---|---:|---:|---:|---:|
| Q1 (Jan 2027 – Mar 2027) | EUR 36,246 | EUR 6,500 | EUR 6,412 | EUR 49,158 |
| Q2 (Apr 2027 – Jun 2027) | EUR 36,246 | EUR 0 | EUR 5,437 | EUR 41,683 |
| Q3 (Jul 2027 – Sep 2027) | EUR 36,246 | EUR 0 | EUR 5,437 | EUR 41,683 |
| Q4 (Oct 2027 – Dec 2027) | EUR 36,246 | EUR 0 | EUR 5,437 | EUR 41,683 |
| **Year** | **EUR 144,984** | **EUR 6,500** | **EUR 22,723** | **EUR 174,207** |

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

[1-Year Forecast](forecast-1yr.md) · [Stakeholders and RACI](stakeholders-raci.md)

## Assumptions and open questions

| # | Item | Type | Why unverified | Who can confirm |
|---|------|------|----------------|-----------------|
| A1 | All rates and costs are sample values | assumption | demonstration run | finance |
| A2 | Product photography lands in Q1 | assumption | no month given | product owner |
| Q1 | Is the backend API (`VITE_API_URL`) budgeted elsewhere? | open question | backend not in this repo | engineering lead |
