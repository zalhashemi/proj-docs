---
title: Developer Guide
subtitle: "{{project_name}}"
version: 1.0.0
date: "{{YYYY-MM-DD}}"
author: "{{author}}"
project: "{{project_name}}"
doc_id: dev-guide
confidential: false
---

<!-- guide: Audience: a developer on day one. Terse and precise. Every command must come
from the repo (package.json scripts, Makefile, justfile, pyproject, README). Run the safe ones
(--help, --version, lint, test --listOnly / dry-run) and paste short real output. Mark every
command you did not run with ⟨untested⟩. Never run install scripts that modify the system,
migrations against real DBs, or deploys. -->

## Prerequisites

<!-- guide: Versions from .nvmrc, .tool-versions, .python-version, engines field, go.mod,
rust-toolchain, Dockerfile FROM. Cite the file for each. -->

| Tool | Version | Source |
|---|---|---|
| {{tool}} | {{version}} | `{{file}}` |

## Clone to running

<!-- guide: Numbered, copy-pasteable. Include env setup (copy .env.example), install,
DB/services (docker compose up), run. Each step: command + what success looks like. -->

1. Clone and enter the repo:

   ```bash
   git clone {{remote_url}}
   cd {{repo_dir}}
   ```

2. Configure environment:

   ```bash
   cp .env.example .env
   ```

   Fill in the required variables. See [Environment and Configuration Reference](env-config-reference.md).

3. Install dependencies:

   ```bash
   {{install command}}
   ```

4. Start backing services:

   ```bash
   {{e.g. docker compose up -d db}}
   ```

5. Run the app:

   ```bash
   {{dev command}}
   ```

   Expected: {{e.g. "Listening on http://localhost:3000"}}

## Project structure

<!-- guide: Top 2 levels only, with one-line purpose per entry. Skip generated folders. -->

```text
{{tree}}
```

## Common workflows

<!-- guide: Table of every script/target with what it does. Then short recipes for the
3–5 most common tasks (add an endpoint, add a migration, add a component…), grounded in the
existing code patterns (cite an example file to copy). -->

| Command | What it does | Tested |
|---|---|---|
| `{{command}}` | {{purpose}} | ✓ / ⟨untested⟩ |

### {{Recipe: e.g. Add a new API endpoint}}

1. {{step}} (see `{{example file}}`)

## Testing

```bash
{{test command}}
```

Details: [Testing Strategy](testing-strategy.md).

## Debugging tips

<!-- guide: Real ones: debug configs in .vscode/launch.json, log level env vars, verbose
flags, how to inspect the DB, common errors seen in code (custom error classes). -->

- {{tip}}

## Related documents

[Architecture](architecture.md) · [Environment and Configuration Reference](env-config-reference.md) · [Testing Strategy](testing-strategy.md) · [Contributing](contributing.md)

## Assumptions and open questions

| # | Item | Type | Why unverified | Who can confirm |
|---|------|------|----------------|-----------------|
| A1 | {{item}} | assumption | {{reason}} | {{role}} |
