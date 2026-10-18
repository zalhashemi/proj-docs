# Workflow details

Load this when you need more than SKILL.md gives you.

## Files the skill owns (inside the target project)

| Path | Written by | Purpose |
|---|---|---|
| `docs/<id>.md` | Claude | Source of truth for each doc; the user may edit it |
| `docs/pdf/<id>.pdf`, `docs/pdf/docs-pack.pdf` | build_pdf.py | Rendered output |
| `docs/.project-docs/scan.json` | scan_project.py | Repo facts |
| `docs/.project-docs/theme.json` | detect_theme.py / user choice | Final theme |
| `docs/.project-docs/inputs.yaml` | Claude | User answers to `required_inputs` (`unknown` allowed) |
| `docs/.project-docs/state.json` | state.py | Stage, per-doc hashes, versions |
| `docs/.project-docs/assets/` | finance.py, build_pdf.py | Charts, rendered diagrams |
| `docs/.project-docs/preview/` | verify_pdf.py | PNG thumbnails |

Everything is regenerated in place. Running twice overwrites the same paths, never `-2` copies.

## Scanning tips

Exclude sample or fixture projects with `--exclude 'path/to/fixtures/*'` (works for both
`scan_project.py` and `detect_theme.py`). Otherwise their routes, env vars and colours get
mixed into the real project.

## Catalog fields

- `sources_to_scan`: globs, files or commands to read for this doc. Read only these plus
  `scan.json`, so context stays small.
- `required_inputs`: `{key, question, type (text|number|choice|multi|bool|money|list), default, choices?}`.
  Skip any input the scan already answers. Inputs shared between docs (like `currency`) are asked once.
- `scan_keys`: top-level `scan.json` keys whose change should trigger an update of this doc.
- `stage`: `planning` (build-plan only), `complete` (default), or `any`.
- `depends_on`: docs to cross-link. Link as `[Architecture](architecture.md)`; build_pdf
  rewrites these as in-pack links when combining.

## Drafting a doc

1. Copy the template's front matter. Set `title`, `subtitle`, `version: 1.0.0`, `date: YYYY-MM-DD`,
   `author` (from inputs, or git's top contributor if the user agrees, else `⟨assumption⟩`),
   `project`, and `confidential` if the user asked for it.
2. Keep the template's section order. Delete sections that truly don't apply
   (e.g. "Database" for a static site) and say so in one line instead of leaving them empty.
3. Replace each `{{placeholder}}` with evidence-backed content. Placeholders the repo and
   inputs can't fill become `⟨assumption⟩` values or open questions. Never leave a raw `{{…}}` behind.
4. Keep diagrams in Mermaid (` ```mermaid `).
5. Finish with the assumptions appendix (see writing-standards.md §2).

## No-UI adaptation

When `has_ui` is false and the user selected `user-guide` or `quick-start`, use the template's
`<!-- variant: cli-api -->` sections. These are task-oriented flows using the CLI commands or
API calls (curl examples) found in the scan. Tell the user: "No UI found, so the user guide
covers CLI/API usage instead."

## Financial docs

`finance.py` reads `inputs.yaml` and prints Markdown (inputs table, formulas, scenario
outputs, quarterly totals) plus chart PNGs coloured from theme.json. Paste its output
verbatim. If an input is `unknown`, the script uses the catalog default and marks it as an assumption.

## Rendering notes

- `build_pdf.py` options: `--theme`, `--out`, `--renderer weasyprint|chromium`, `--page-size a4|letter`,
  `--combine`, `--no-cover`, `--no-toc`. It prints JSON (`{"outputs": [...], "renderer": ..., "warnings": [...]}`).
- WeasyPrint needs Pango. If it can't import, the build falls back to Chromium and says so.
- Mermaid: pre-rendered to SVG with `mmdc` if it's on PATH. Otherwise the block shows as code
  with a visible "diagram not rendered" note. One bad diagram never fails the build.

## Verify checklist

`verify_pdf.py` exits nonzero on: a blank page, text outside the margins, a font that isn't
embedded, a missing TOC or a broken internal link, or a theme contrast below 4.5:1. Common fixes:

| Problem | Fix |
|---|---|
| Table overflows the margin | Fewer columns, shorter cell text, or move detail to a list |
| Long unbroken string (hash, URL) | Wrap it in backticks; CSS lets inline code break anywhere |
| Heading alone at the bottom of a page | Usually auto-handled; otherwise add `<div class="page-break"></div>` before it |
| Blank page | Remove trailing manual page breaks |

## Update mode in practice

`state.py diff` prints JSON like:

```json
{"stage": "complete",
 "changed": [
  {"doc": "api-reference", "keys": ["routes"], "summary": ["route PATCH /orders/{order_id} added"],
   "hand_edited": false, "needs_patch": true},
  {"doc": "data-model", "keys": [], "summary": [], "hand_edited": true, "needs_patch": false}],
 "unchanged": 12, "missing_markdown": [], "untracked": []}
```

- `needs_patch: true`: find the sections that cover the changed facts and edit them in place.
  Then run `state.py bump <id>` (x.y.z → x.y.(z+1), date → today), re-render only that doc,
  and run `state.py record --doc <id>`.
- `hand_edited: true`: the user changed the Markdown since it was generated. Keep their text.
  If it also needs a patch, show the patch as a diff and wait for approval.
  If it only has hand edits, just re-render (their edits should reach the PDF) and record it.
- `untracked`: Markdown in `docs/` that the skill didn't generate. Leave it alone unless asked.
- `stage_suggestion`: the project gained code since the build plan, so ask whether it's complete.
