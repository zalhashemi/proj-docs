---
title: 1-Year Forecast
subtitle: "Trailmate"
version: 1.0.0
date: "2026-10-18"
author: "Trailmate team"
project: "Trailmate"
doc_id: forecast-1yr
confidential: true
---

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


## Related documents

[Budget and Resource Plan](budget-resources.md)

## Assumptions and open questions

| # | Item | Type | Why unverified | Who can confirm |
|---|------|------|----------------|-----------------|
| A1 | All forecast inputs are sample values | assumption | demonstration run | product owner |
