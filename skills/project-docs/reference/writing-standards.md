# Writing standards

These rules are what make generated docs trustworthy. A reader must be able to tell
**verified fact** from **assumption** at a glance, so every rule below serves that goal.

## 1. Never fabricate

Do not state as true anything the repo doesn't show and the user didn't say. That covers versions,
endpoints, people and roles, costs, user numbers, SLAs, uptime, compliance status,
customers and dates. If the content is needed but unknown, write it as an assumption (section 2)
or an open question. A clearly labelled gap is useful. A plausible invention is harmful,
because readers act on it.

Evidence, strongest first: code and config in the repo → scan.json → git history →
the user's answers in `inputs.yaml` → existing docs (README and similar), which may be stale,
so say so if they conflict with the code.

## 2. Mark assumptions

Block form, for a paragraph or table built on an assumption:

```markdown
> [!ASSUMPTION]
> Traffic grows 10%/month. Nothing in the repo or inputs states a growth rate.
```

Inline form, for a single value: `Peak load is ~200 req/s ⟨assumption⟩.`

Every pack ends with this chapter. It names the chapters left out, then repeats each assumption
in one line plus the open questions, for the whole pack:

```markdown
# Assumptions and open questions {#ch-assumptions}

Not included: Data Model (no database found), Integration Guide (no openapi or routes found).

| # | Chapter | Item | Type | Why unverified | Who can confirm |
|---|---------|------|------|----------------|-----------------|
| A1 | 1-Year Forecast | 10%/month growth | assumption | not in repo or inputs | product owner |
| Q1 | Runbook | Who owns on-call? | open question | no CODEOWNERS / inputs | eng manager |
```

If there are none, write "None. Every statement is backed by repo evidence or user input."

Other callouts: `> [!NOTE]`, `> [!TIP]`, `> [!WARNING]`. Each one renders in its own colour.

## 3. Financial documents (forecast-1yr, budget-resources)

- Order: **inputs table → formulas → outputs**. `scripts/finance.py` computes everything.
  Don't do arithmetic by hand.
- State the currency and period on the first table ("USD, monthly, Jan–Dec 2027").
- Use ranges, not point estimates, unless the user gave a fixed number. Label the scenarios
  **Conservative / Base / Optimistic**.
- Include this one-line disclaimer under the title: *Planning estimates only, not financial advice.*

## 4. Security-sensitive content

- Never print secret values. List env vars by **name, type, purpose and whether required**.
- If a config file contains something token-like, write `«redacted»` and flag it in the
  assumptions appendix as a possible committed secret.
- Threat models describe classes of weakness and mitigations, not working exploits.

## 5. Legal-adjacent documents

Privacy, compliance checklists, SLAs and anything mentioning GDPR, SOC 2 or HIPAA are
**templates and checklists, not legal advice**. Put this line under the title:
*Template for discussion with qualified counsel. Not legal advice.* Never mark a control
"compliant". Use: `evidence found` (with a path), `not found`, or `needs review`.

## 6. Concrete beats generic

- Use real commands from `package.json` scripts, the Makefile, justfile or pyproject, and real
  file paths. Prefer a copy-pasteable command block to a sentence describing it.
- dev-guide: run safe commands (`--help`, `--version`, lint, test dry-runs) and keep their
  real output short. Mark anything you didn't run with `⟨untested⟩`.
- Cite evidence inline: "Auth uses JWT (`src/middleware/auth.ts`)".

## 7. Tone and format

- Write clearly and concisely, in active voice. No filler ("In today's fast-paced world"),
  no marketing words ("seamless", "robust", "cutting-edge").
- Match the audience. Dev and ops docs are precise and terse. User docs are friendly,
  second person and task-based ("To export a report, …"). Business docs lead with the
  decision or number.
- Use tables for anything with 3+ comparable attributes. Keep them to 6 columns or fewer;
  split wide tables or move detail into notes, because wide tables overflow A4.
  Put units in the headers, not the cells.
- Headings: one `#` (the title, from front matter), `##` sections, `###` subsections. Don't go
  deeper than `####`.
- Code blocks always carry a language tag so they get syntax highlighting.
- Diagrams: write Mermaid in a fenced code block tagged `mermaid`. It is rendered if `mmdc` exists, otherwise shown
  as code with a note.

## 8. Updates (update mode)

When patching an existing doc, keep its voice and structure. Change only the sentences, rows
or sections the change affects. Never re-word untouched content. Keep the user's manual
edits; a reviewer should see a small, explainable diff.
