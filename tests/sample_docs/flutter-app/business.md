---
title: Business Pack
subtitle: Trailmate
version: 1.0.0
date: '2026-10-18'
author: Trailmate team
project: Trailmate
pack: business
chapters:
- forecast-1yr
- budget-resources
confidential: false
---

# 1-Year Forecast {#ch-forecast-1yr}

*Planning estimates only, not financial advice.*

> [!NOTE]
> These figures use **sample inputs** supplied to demonstrate the skill. They are not real Trailmate data.

Trailmate stores data in Cloud Firestore (`cloud_firestore` in `pubspec.yaml`), so infrastructure cost is Firebase usage. No revenue model was given.


## Assumptions

Currency: **USD**. Period: **monthly, Jan 2027 – Dec 2027**.

| Input | Value | Source | Assumption |
|---|---|---|---|
| `currency` | USD | user | — |
| `forecast_start` | 2027-01 | user | — |
| `starting_users` | 500 | user | — |
| `monthly_growth_pct` | 5-15 | user | — |
| `infra_cost_per_user` | 0.03 | user | — |
| `fixed_infra_cost` | 25 | user | — |
| `revenue_model` | none | user | — |

## Method

```text
users[m]   = starting_users × (1 + growth)^m          (m = 0..11)
infra[m]   = fixed_infra_cost + users[m] × infra_cost_per_user
```

## Scenarios

| Scenario | Growth / month | Conversion |
|---|---|---|
| Conservative | 5% | — |
| Base | 10% | — |
| Optimistic | 15% | — |

## Users and usage

![Active users by scenario](.project-docs/assets/forecast-users.png)

| Month | Conservative | Base | Optimistic |
|---|---:|---:|---:|
| Jan 2027 | 500 | 500 | 500 |
| Feb 2027 | 525 | 550 | 575 |
| Mar 2027 | 551 | 605 | 661 |
| Apr 2027 | 579 | 666 | 760 |
| May 2027 | 608 | 732 | 875 |
| Jun 2027 | 638 | 805 | 1,006 |
| Jul 2027 | 670 | 886 | 1,157 |
| Aug 2027 | 704 | 974 | 1,330 |
| Sep 2027 | 739 | 1,072 | 1,530 |
| Oct 2027 | 776 | 1,179 | 1,759 |
| Nov 2027 | 814 | 1,297 | 2,023 |
| Dec 2027 | 855 | 1,427 | 2,326 |

## Infrastructure cost

![Monthly infrastructure cost (USD)](.project-docs/assets/forecast-cost.png)

| Month | Conservative | Base | Optimistic |
|---|---:|---:|---:|
| Jan 2027 | USD 40 | USD 40 | USD 40 |
| Feb 2027 | USD 41 | USD 42 | USD 42 |
| Mar 2027 | USD 42 | USD 43 | USD 45 |
| Apr 2027 | USD 42 | USD 45 | USD 48 |
| May 2027 | USD 43 | USD 47 | USD 51 |
| Jun 2027 | USD 44 | USD 49 | USD 55 |
| Jul 2027 | USD 45 | USD 52 | USD 60 |
| Aug 2027 | USD 46 | USD 54 | USD 65 |
| Sep 2027 | USD 47 | USD 57 | USD 71 |
| Oct 2027 | USD 48 | USD 60 | USD 78 |
| Nov 2027 | USD 49 | USD 64 | USD 86 |
| Dec 2027 | USD 51 | USD 68 | USD 95 |

## Revenue

No revenue model was provided, so revenue is not projected.

## Summary

| Metric (year 1) | Conservative | Base | Optimistic | Range |
|---|---:|---:|---:|---|
| Active users at month 12 | 855 | 1,427 | 2,326 | 855 – 2,326 |
| Total infra cost | USD 539 | USD 621 | USD 735 | USD 539 – USD 735 |

## What would change this forecast

- Each extra percentage point of monthly growth adds about **149** users by month 12 (base scenario).
- Infrastructure cost scales linearly with users; a cheaper tier or caching lowers `infra_cost_per_user`.

# Budget and Resource Plan {#ch-budget-resources}

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

# Assumptions and open questions {#ch-assumptions}

Not included: Project Brief, Product Requirements Document, Roadmap, Risk Register, Competitive Analysis (not selected for this sample).

| # | Chapter | Item | Type | Why unverified | Who can confirm |
|---|---|---|---|---|---|
| A1 | 1-Year Forecast | All forecast inputs are sample values | assumption | demonstration run | product owner |
| A2 | Budget and Resource Plan | Contingency % not provided; default 15% used | assumption | answered "unknown" | product owner |
| A3 | Budget and Resource Plan | Store fees land in Q1 | assumption | no month given | product owner |
