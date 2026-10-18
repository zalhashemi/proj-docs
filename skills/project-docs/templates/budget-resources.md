---
title: Budget and Resource Plan
subtitle: "{{project_name}}"
version: 1.0.0
date: "{{YYYY-MM-DD}}"
author: "{{author}}"
project: "{{project_name}}"
doc_id: budget-resources
confidential: true
---

*Planning estimates only, not financial advice.*

<!-- guide: Do NOT add up anything yourself. Run:
  $PY $SKILL/scripts/finance.py budget --inputs docs/.project-docs/inputs.yaml --theme docs/.project-docs/theme.json
and paste its tables. Infra/tooling line items can be suggested from the scan (managed DB,
hosting config, SaaS SDKs) but their costs come from inputs or are marked ⟨assumption⟩. -->

## Inputs

{{finance.py inputs table: currency, period, contingency %, sources}}

## Team

<!-- guide: Roles × allocation × monthly rate = monthly cost (computed by script). -->

{{finance.py team table}}

## Infrastructure and tooling

<!-- guide: Recurring monthly items. Suggest items found in the repo (e.g. "Postgres: docker-compose.yml, Sentry SDK in package.json"). -->

{{finance.py recurring table}}

## Licences and one-time costs

{{finance.py one-time table}}

## Contingency

{{finance.py contingency line: contingency % × subtotal}}

## Totals by quarter

{{finance.py quarterly table: one-time vs recurring, Q1–Q4, year total}}

{{finance.py quarterly chart}}

## Formulas

{{finance.py formulas block}}

## Related documents

[1-Year Forecast](forecast-1yr.md) · [Stakeholders and RACI](stakeholders-raci.md)

## Assumptions and open questions

| # | Item | Type | Why unverified | Who can confirm |
|---|------|------|----------------|-----------------|
| A1 | {{item}} | assumption | {{reason}} | {{role}} |
