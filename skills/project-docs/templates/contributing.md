---
title: Contributing Guide
subtitle: "{{project_name}}"
version: 1.0.0
date: "{{YYYY-MM-DD}}"
author: "{{author}}"
project: "{{project_name}}"
doc_id: contributing
confidential: false
---

<!-- guide: Infer conventions from evidence, not wishes: branch names from git, commit style
from the last 50 commit subjects (e.g. ≥70% match "type(scope): …" → Conventional Commits),
lint/format from configs, checks from CI. If an existing CONTRIBUTING.md exists, extend it and
note any conflicts with what the history shows. -->

## Workflow

1. Create a branch from `{{default branch}}`: `{{branch naming pattern}}`
2. Make changes; run checks locally (below).
3. Open a pull request against `{{default branch}}`.

## Branching

| Branch | Purpose | Evidence |
|---|---|---|
| `{{main}}` | {{purpose}} | {{git}} |

## Commit messages

<!-- guide: Show 2–3 real commit subjects as examples. -->

Style: {{Conventional Commits / imperative free-form}} ({{x}}% of the last 50 commits match)

```text
{{real example}}
```

## Code style

| Tool | Config | Command |
|---|---|---|
| {{eslint/ruff/prettier}} | `{{config file}}` | `{{command}}` |

## Checks before opening a PR

- [ ] `{{lint command}}` passes
- [ ] `{{test command}}` passes
- [ ] {{type check / build}}
- [ ] Docs updated if behaviour changed

## Pull request checklist

<!-- guide: From .github/PULL_REQUEST_TEMPLATE if present, else a sensible minimal list. -->

- [ ] Description explains why the change is needed
- [ ] Tests cover the change
- [ ] {{item}}

## Review process

<!-- guide: Required checks from CI config, CODEOWNERS for reviewers. Branch protection isn't visible in the repo, so mark it ⟨assumption⟩. -->

{{review process}}

## Related documents

[Developer Guide](dev-guide.md) · [Testing Strategy](testing-strategy.md)

## Assumptions and open questions

| # | Item | Type | Why unverified | Who can confirm |
|---|------|------|----------------|-----------------|
| A1 | {{item}} | assumption | {{reason}} | {{role}} |
