---
title: Troubleshooting and FAQ
subtitle: "{{project_name}}"
version: 1.0.0
date: "{{YYYY-MM-DD}}"
author: "{{author}}"
project: "{{project_name}}"
doc_id: troubleshooting-faq
confidential: false
---

<!-- guide: Problems must be plausible for THIS code: error messages thrown in source, required
env vars, ports, services in compose, known README gotchas. Quote real error strings. -->

## Troubleshooting

<!-- guide: 6–12 entries. Order by how often they are likely to happen (setup issues first). -->

### `{{exact error message}}`

- **Cause:** {{cause}} (`{{where it's raised}}`)
- **Fix:**

  ```bash
  {{command}}
  ```

## Frequently asked questions

<!-- guide: 5–10 Q&As a new user/dev would actually ask. Answers point to the relevant doc. -->

**{{Question}}**
{{Answer}}. See [{{doc}}]({{doc}}.md).

## Getting more help

{{support channel, issue tracker link from git remote}}

## Related documents

[Runbook](runbook.md) · [Developer Guide](dev-guide.md)

## Assumptions and open questions

| # | Item | Type | Why unverified | Who can confirm |
|---|------|------|----------------|-----------------|
| A1 | {{item}} | assumption | {{reason}} | {{role}} |
