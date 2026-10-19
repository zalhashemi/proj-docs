---
name: project-docs
description: >-
  Generate project documentation from a real codebase as one Markdown pack per category
  (Planning, Developer, Business, User, Ops, Handover and Governance), rendered to a branded
  PDF on request. Chapters cover a build plan before the project exists, then dev guide,
  architecture, API reference, data model, runbook, user guide, onboarding, handover, PRD,
  roadmap, 1-year forecast, budget and resource plan, risk register, compliance checklists and
  more (37 chapter types). PDFs use the project's own colors, fonts and logo, or a default
  theme. Also updates existing packs in place when the project changes. Use whenever the user asks for project documentation, a docs pack,
  "generate PDFs for this project", or any of the documents above, even without saying "PDF".
  Not for a single README edit, inline code comments or docstrings.
when_to_use: >-
  "document this project", "make a docs pack", "write handover docs", "create a runbook",
  "user guide for the app", "1-year forecast", "budget and resource plan", "build plan",
  "update the docs", "refresh the PDFs".
---

# project-docs

Turn a repository into a few evidence-based Markdown packs, and into branded PDFs when asked.

`$SKILL` = `${CLAUDE_SKILL_DIR}`. All output stays inside the target project: one `docs/<pack>.md`
per selected pack, PDFs in `docs/pdf/` (only on request), state in `docs/.project-docs/`. Never write
outside `docs/` without asking. Never commit. Write nothing beyond what this file lists: no per-chapter
files, no extra packs, no PDFs nobody asked for.
Read `reference/writing-standards.md` before drafting: its no-fabrication rules make the docs trustworthy.

## 0. Environment and mode

Run `python3 $SKILL/scripts/bootstrap.py` (`python` on Windows). Use its `python` value as
`$PY` for every script. If `ready` is false, ask the user before running it again with
`--install`, because that downloads packages. Add `--with-chromium` if the user has neither Pango
nor Chrome. Then: `docs/.project-docs/state.json` exists → **update mode** (section 9); otherwise this is a first run.

## 1. Scan

```bash
$PY $SKILL/scripts/scan_project.py <project> --out docs/.project-docs/scan.json
$PY $SKILL/scripts/state.py packs      # per pack: chapters the scan supports, and those skipped (why)
```
Skim the JSON summary: project type, `has_ui`, stack, `stage_hint`.

## 2. Stage: Planning pack first, the rest when complete

- **planning**: the project isn't built yet. Expect `stage_hint: planning` (few or no source
  files, few commits); confirm it with the user. Write only the `planning` pack.
- **complete**: the user says the project is finished, or confirms it when you ask. Offer the
  other packs (section 3).
- A user who explicitly asks for a specific pack or chapter gets it in any stage. Note in the
  assumptions chapter that the project was still in progress.

Record the stage with `$PY $SKILL/scripts/state.py set-stage <planning|complete>`.

## 3. Select packs (complete stage)

Read `catalog.yaml` (`packs` and `docs`; each doc is a chapter of exactly one pack). Ask once with
`AskUserQuestion`, two multi-select questions in one call: **Q1** Developer, Business, User, Ops;
**Q2** Handover and Governance, None. Show each pack's chapter count from `state.py packs`.
Write only the packs the user picks.

Chapters per pack: start from `state.py packs` → `chapters`. Its `skipped` chapters (failed `needs`)
stay out. Also leave out any chapter that has neither repo evidence nor user answers to its
`required_inputs` (e.g. a forecast with every input unknown). Don't add chapters to fill a pack.
If `has_ui` is false, `user-guide` and `quick-start` use the template's CLI/API variant. **Tell the user.**

## 4. Theme

```bash
$PY $SKILL/scripts/detect_theme.py <project> --out docs/.project-docs/theme.json
```

- **UI detected:** show the palette, fonts, logo and confidence levels, plus any contrast
  fixes or dark-to-light mapping. Ask the user to confirm, tweak, or pick a default theme.
- **No UI, or the user declines:** offer the defaults in `themes/`. Render
  `scripts/preview_themes.py` swatches if they want to compare.
- Always write the final choice to `docs/.project-docs/theme.json`. If a detected font isn't
  bundled, tell the user which bundled font replaces it.

Details: `reference/theme-detection.md`.

## 5. Gather inputs

Collect the `required_inputs` of the included chapters only, minus anything the scan already answers.
Ask in batches of up to 4, offer each `default`, and accept "unknown". Unknowns become
assumptions, never invented facts. Save the answers to `docs/.project-docs/inputs.yaml`.

## 6. Draft `docs/<pack>.md`

One file per pack. Front matter: `title` (the pack title), `subtitle`, `version: 1.0.0`, `date`,
`author`, `project`, `pack: <id>`, `chapters: [<ids in catalog order>]`, `confidential`. Then, per chapter:

- `# <Chapter title> {#ch-<id>}`, then the body of `templates/<template>` (drop its front matter,
  its "Related documents" section and its assumptions section). Read only the template's
  `sources_to_scan`, plus `scan.json`.
- Ground every claim in the repo and cite paths (`src/api/orders.ts`). Follow the
  `<!-- guide: -->` comments; they are stripped at render time.
- Link to another chapter in the same pack as `[Architecture](#ch-architecture)`. Name a chapter in
  another pack in plain text ("see the Ops pack, Runbook").
- For `forecast-1yr` and `budget-resources`, never do the arithmetic yourself. Run
  `$PY $SKILL/scripts/finance.py <forecast|budget> --inputs docs/.project-docs/inputs.yaml`
  and paste its tables and chart paths.
- For `dev-guide`, run safe commands (`--help`, lint, dry-run) and mark any command you didn't
  run with `⟨untested⟩`.

End the pack with one `# Assumptions and open questions {#ch-assumptions}` chapter: a single
"Not included:" line naming the chapters left out and why, then one table for the whole pack
(`reference/writing-standards.md` §2). Detailed drafting rules: `reference/workflow-details.md`.

## 7. Record and report

Run `$PY $SKILL/scripts/state.py record`, then stop. Report the pack files written, chapters
left out (and why), docs adapted for no-UI projects, and a short **Open assumptions and missing
inputs** list. Offer the PDF in one line. **Don't render unless the user asks.**

## 8. PDF, only when asked

```bash
$PY $SKILL/scripts/build_pdf.py docs/<pack>.md --theme docs/.project-docs/theme.json --out docs/pdf/
$PY $SKILL/scripts/verify_pdf.py docs/pdf/<pack>.pdf --theme docs/.project-docs/theme.json
```

Render only the packs the user named. Combine (`docs/*.md --combine`) only if they ask for a single
file. WeasyPrint is the default renderer. Use `--renderer chromium` for Mermaid or JS-heavy docs;
the script falls back automatically and says so. Fix every verify failure, then open the PNGs in
`docs/.project-docs/preview/`: the cover, one table-heavy page and one code-heavy page.

## 9. Update mode: add or adjust, never rewrite

When the project changes, update the packs the way a careful editor would: touch only what changed.

```bash
$PY $SKILL/scripts/scan_project.py <project> --out docs/.project-docs/scan.json
$PY $SKILL/scripts/state.py diff
```

`diff` lists only the packs whose watched scan keys changed, and per pack the affected
**chapters** with what changed (e.g. "route `POST /orders` added"). It also flags hand-edited packs
and skipped chapters that now have evidence (`included: false`). For each affected pack:

- Patch **only the affected chapter sections** with the Edit tool: add a table row, fix a command,
  add a subsection. Don't redraft or "improve" untouched prose. Offer newly supported chapters; add
  one (and its id in `chapters:`) only if the user agrees.
- If the pack was hand-edited, show the proposed patch as a diff and apply it only after the
  user approves.
- Bump version and date with `$PY $SKILL/scripts/state.py bump <pack>`, then `state.py record --pack <pack>`.
- Re-render a pack only if `docs/pdf/<pack>.pdf` already exists (plus a combined PDF if one exists).

If the stage moved from planning to complete, offer the pack selection. Leave `planning` as it is.
If nothing relevant changed, say so and stop.
