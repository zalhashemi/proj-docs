---
name: project-docs
description: >-
  Generate branded PDF project documentation from a real codebase: a build plan before the
  project exists, then dev guide, architecture doc, API reference, data model, runbook, user
  guide, onboarding docs, handover docs, PRD, roadmap, 1-year forecast, budget and resource
  plan, risk register, compliance checklists and more (37 doc types, grouped into Developer,
  Business, User, Ops and Handover packs). Styles every PDF with the project's own colors,
  fonts and logo, or with a default theme. Also updates existing docs in place when the
  project changes. Use whenever the user asks for project documentation, a docs pack,
  "generate PDFs for this project", or any of the documents above, even without saying "PDF".
  Not for a single README edit, inline code comments or docstrings.
when_to_use: >-
  "document this project", "make a docs pack", "write handover docs", "create a runbook",
  "user guide for the app", "1-year forecast", "budget and resource plan", "build plan",
  "update the docs", "refresh the PDFs".
---

# project-docs

Turn a repository into a set of branded, evidence-based PDF documents.

`$SKILL` = `${CLAUDE_SKILL_DIR}`. All output stays inside the target project: Markdown in `docs/`,
PDFs in `docs/pdf/`, state in `docs/.project-docs/`. Never write outside `docs/` without asking. Never commit.
Read `reference/writing-standards.md` before drafting: its no-fabrication rules make the docs trustworthy.

## 0. Environment and mode

Run `python3 $SKILL/scripts/bootstrap.py` (`python` on Windows). Use its `python` value as
`$PY` for every script. If `ready` is false, ask the user before running it again with
`--install`, because that downloads packages. Add `--with-chromium` if the user has neither Pango
nor Chrome. Then: `docs/.project-docs/state.json` exists → **update mode** (section 9); otherwise this is a first run.

## 1. Scan

```bash
$PY $SKILL/scripts/scan_project.py <project> --out docs/.project-docs/scan.json
```

Skim the JSON summary: project type, `has_ui`, stack, `stage_hint`.

## 2. Stage: build plan first, everything else when complete

Docs follow the project lifecycle so you don't produce 40 PDFs about code that doesn't exist yet.

- **planning**: the project isn't built yet. Expect `stage_hint: planning` (few or no source
  files, few commits); confirm it with the user. Offer only `build-plan` (catalog `stage: planning`).
- **complete**: the user says the project is finished, or confirms it when you ask. Offer
  the full catalog (section 3).
- A user who explicitly asks for a specific document gets it in any stage. Note in the doc's
  assumptions appendix that the project was still in progress.

Record the stage with `$PY $SKILL/scripts/state.py set-stage <planning|complete>`.

## 3. Select documents (complete stage)

Read `catalog.yaml` (entries plus `presets`). Use `AskUserQuestion` with at most 4 options
per question:

1. **Q1 (pack):** Developer, Business, User, Ops. **Q2:** Handover, Everything, Custom.
2. For **Custom**, ask one multi-select question per audience group, 4 docs each, over as
   many questions as needed.

Show each doc's `est_pages`. Add the `depends_on` docs only if the user agrees.
If `has_ui` is false, `user-guide` and `quick-start` use the template's CLI/API variant.
**Tell the user** you did that.

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

Collect the `required_inputs` of the selected docs, minus anything the scan already answers.
Ask in batches of up to 4, offer each `default`, and accept "unknown". Unknowns become
assumptions, never invented facts. Save the answers to `docs/.project-docs/inputs.yaml`.

## 6. Draft

For each doc, in dependency order:

- Start from `templates/<template>`. Read only the `sources_to_scan` it lists, plus `scan.json`.
- Write `docs/<id>.md`. Keep the template's front matter and fill in title, version and date.
- Ground every claim in the repo and cite paths (`src/api/orders.ts`). Follow the
  `<!-- guide: -->` comments; they are stripped at render time.
- For `forecast-1yr` and `budget-resources`, never do the arithmetic yourself. Run
  `$PY $SKILL/scripts/finance.py <forecast|budget> --inputs docs/.project-docs/inputs.yaml`
  and paste its tables and chart paths.
- For `dev-guide`, run safe commands (`--help`, lint, dry-run) and mark any command you didn't
  run with `⟨untested⟩`.
- End each doc with the "Assumptions and open questions" appendix.

Detailed drafting rules: `reference/workflow-details.md`.

## 7. Render

```bash
$PY $SKILL/scripts/build_pdf.py docs/<id>.md --theme docs/.project-docs/theme.json --out docs/pdf/
$PY $SKILL/scripts/build_pdf.py docs/*.md --combine --out docs/pdf/docs-pack.pdf   # optional
```

WeasyPrint is the default renderer. Use `--renderer chromium` for Mermaid or JS-heavy docs.
The script falls back automatically and says so. Offer the combined pack.

## 8. Verify and report

```bash
$PY $SKILL/scripts/verify_pdf.py docs/pdf/*.pdf --theme docs/.project-docs/theme.json
```

Fix every failure. Open the PNGs in `docs/.project-docs/preview/` and look at least at the
cover, one table-heavy page and one code-heavy page. Then run
`$PY $SKILL/scripts/state.py record` to store hashes for later updates.

Report: output paths, the theme used, docs adapted for no-UI projects, and a short
**Open assumptions and missing inputs** list.

## 9. Update mode: add or adjust, never rewrite

When the project changes, update the docs the way a careful editor would: touch only what changed.

```bash
$PY $SKILL/scripts/scan_project.py <project> --out docs/.project-docs/scan.json
$PY $SKILL/scripts/state.py diff
```

`diff` lists only the docs whose `scan_keys` changed, and what changed (e.g. "route
`POST /orders` added"). It also flags docs the user hand-edited. For each affected doc:

- Patch **only the affected sections** with the Edit tool: add a table row, fix a command,
  add a subsection. Don't redraft the doc or "improve" untouched prose.
- If the doc was hand-edited, show the proposed patch as a diff and apply it only after the
  user approves.
- Bump version and date with `$PY $SKILL/scripts/state.py bump <id>`.
- Re-render only the patched docs, plus the combined pack if one exists. Then run `state.py record`.

If the stage moved from planning to complete, offer the full catalog. Leave `build-plan` as it is.
If nothing relevant changed, say so and stop.
