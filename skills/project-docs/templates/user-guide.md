---
title: User Guide
subtitle: "{{project_name}}"
version: 1.0.0
date: "{{YYYY-MM-DD}}"
author: "{{author}}"
project: "{{project_name}}"
doc_id: user-guide
confidential: false
---

<!-- guide: Task-oriented, not feature-oriented: organise by what users want to get done.
Friendly, second person, short steps. Use the variant that matches scan.has_ui and delete the
other variant entirely. -->

<!-- variant: ui -->

## Getting started

{{how to access: URL / app store / install; how to sign in}}

## Tasks

<!-- guide: One section per user task, derived from pages/screens/routes. Steps reference visible
UI labels found in components (button text, page titles). 5–10 tasks. -->

### {{To do X}}

1. Open **{{page}}**.
2. Click **{{button label}}**.
3. {{result}}

> [!TIP]
> {{shortcut or helpful hint}}

## Account and settings

{{profile, password, notifications}}

<!-- /variant -->

<!-- variant: cli-api -->

> [!NOTE]
> {{project_name}} has no graphical interface, so this guide covers using it through its {{command line / HTTP API}}.

## Getting started

```bash
{{install / access command}}
```

## Tasks

<!-- guide: One section per task using CLI commands (from entry points/argparse/click/commander
definitions) or API calls (curl). Show the command plus abbreviated real output. -->

### {{To do X}}

```bash
{{command}}
```

{{what you'll see}}

## Configuration

{{config file / env vars a user may set}}

<!-- /variant -->

## Troubleshooting

See [Troubleshooting and FAQ](troubleshooting-faq.md).

## Related documents

[Quick Start](quick-start.md) · [Troubleshooting and FAQ](troubleshooting-faq.md)

## Assumptions and open questions

| # | Item | Type | Why unverified | Who can confirm |
|---|------|------|----------------|-----------------|
| A1 | {{item}} | assumption | {{reason}} | {{role}} |
