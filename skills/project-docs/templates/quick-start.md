---
title: Quick Start
subtitle: "{{project_name}}"
version: 1.0.0
date: "{{YYYY-MM-DD}}"
author: "{{author}}"
project: "{{project_name}}"
doc_id: quick-start
confidential: false
---

<!-- guide: Zero to first success in ≤5 steps, ≤2 pages. One happy path only. Use the variant
matching scan.has_ui and delete the other. -->

<!-- variant: ui -->

## 1. Open {{project_name}}

{{URL or install}}

## 2. Sign in

{{how}}

## 3. {{First meaningful action}}

{{steps}}

## 4. You're done

{{what success looks like}}. Next: [User Guide](user-guide.md).

<!-- /variant -->

<!-- variant: cli-api -->

> [!NOTE]
> {{project_name}} has no graphical interface. This quick start uses the {{CLI / HTTP API}}.

## 1. Install or start

```bash
{{command}}
```

## 2. Configure

```bash
{{minimal config}}
```

## 3. First call

```bash
{{command or curl}}
```

Expected output:

```text
{{output}}
```

## 4. Next steps

See the [User Guide](user-guide.md).

<!-- /variant -->

## Assumptions and open questions

| # | Item | Type | Why unverified | Who can confirm |
|---|------|------|----------------|-----------------|
| A1 | {{item}} | assumption | {{reason}} | {{role}} |
