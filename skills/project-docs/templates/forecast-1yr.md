---
title: 1-Year Forecast
subtitle: "{{project_name}}"
version: 1.0.0
date: "{{YYYY-MM-DD}}"
author: "{{author}}"
project: "{{project_name}}"
doc_id: forecast-1yr
confidential: true
---

*Planning estimates only, not financial advice.*

<!-- guide: Do NOT compute any number yourself. Run:
  $PY $SKILL/scripts/finance.py forecast --inputs docs/.project-docs/inputs.yaml --theme docs/.project-docs/theme.json
and paste its Markdown output into the sections below. The script marks defaulted inputs as
assumptions. Your job is the narrative: what drives the numbers and what would change them. -->

## Assumptions

<!-- guide: Paste finance.py's "Inputs" table here: every input, its value or range, its
source (user / default / repo), and an assumption flag. Currency and period go in the caption. -->

{{finance.py inputs table}}

> [!ASSUMPTION]
> {{Summarise the inputs that are defaults rather than user-provided.}}

## Method

<!-- guide: Paste finance.py's "Formulas" block. One line per formula, e.g.
users[m] = users[m-1] × (1 + growth); cost[m] = fixed + users[m] × cost_per_user. -->

{{finance.py formulas}}

## Scenarios

| Scenario | Growth / month | Conversion | Notes |
|---|---|---|---|
| Conservative | {{low}} | {{low}} | {{what this assumes}} |
| Base | {{mid}} | {{mid}} | |
| Optimistic | {{high}} | {{high}} | |

## Users and usage

{{finance.py users chart}}

{{finance.py users table (monthly, 3 scenarios)}}

## Infrastructure cost

<!-- guide: Mention what infra the repo shows (Docker, k8s, Terraform resources, managed DB) and how it scales. -->

{{finance.py cost chart}}

{{finance.py cost table}}

## Revenue

<!-- guide: Only if revenue_model is not "none". Otherwise write "No revenue model provided" and skip. -->

{{finance.py revenue chart and table}}

## Summary

<!-- guide: Year-end ranges (Conservative to Optimistic) for users, annual cost, annual revenue and net.
Show ranges, not single numbers. -->

| Metric (year 1) | Conservative | Base | Optimistic |
|---|---|---|---|
| Users at month 12 | | | |
| Total infra cost | | | |
| Total revenue | | | |

## What would change this forecast

- {{sensitivity, e.g. "Each +1% monthly growth adds ~X users by month 12" (from script)}}

## Related documents

[Budget and Resource Plan](budget-resources.md) · [Roadmap](roadmap.md)

## Assumptions and open questions

| # | Item | Type | Why unverified | Who can confirm |
|---|------|------|----------------|-----------------|
| A1 | {{item}} | assumption | {{reason}} | {{role}} |
