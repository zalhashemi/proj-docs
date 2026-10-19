# Workflow details

Load this when you need more than SKILL.md gives you.

## Files the skill owns (inside the target project)

| Path | Written by | Purpose |
|---|---|---|
| `docs/<pack>.md` | Claude | Source of truth, one per selected pack; the user may edit it |
| `docs/pdf/<pack>.pdf`, `docs/pdf/docs-pack.pdf` | build_pdf.py | Rendered output, only when the user asks |
| `docs/.project-docs/scan.json` | scan_project.py | Repo facts |
| `docs/.project-docs/theme.json` | detect_theme.py / user choice | Final theme |
| `docs/.project-docs/inputs.yaml` | Claude | User answers to `required_inputs` (`unknown` allowed) |
| `docs/.project-docs/state.json` | state.py | Stage, per-pack chapters, hashes, versions |
| `docs/.project-docs/assets/` | finance.py, build_pdf.py | Charts, rendered diagrams |
| `docs/.project-docs/preview/` | verify_pdf.py | PNG thumbnails (only after a PDF render) |

Everything is regenerated in place. Running twice overwrites the same paths, never `-2` copies.

## Scanning tips

Exclude sample or fixture projects with `--exclude 'path/to/fixtures/*'` (works for both
`scan_project.py` and `detect_theme.py`). Otherwise their routes, env vars and colours get
mixed into the real project.

## Catalog fields

- `pack`: the one pack this doc is a chapter of. `packs` at the top lists them in menu order.
- `needs`: scan keys of which at least one must hold evidence (a non-empty value), or the chapter
  is skipped. `state.py packs` applies it, so the choice is the same on every run.
- `sources_to_scan`: globs, files or commands to read for this doc. Read only these plus
  `scan.json`, so context stays small.
- `required_inputs`: `{key, question, type (text|number|choice|multi|bool|money|list), default, choices?}`.
  Skip any input the scan already answers. Inputs shared between docs (like `currency`) are asked once.
- `scan_keys`: top-level `scan.json` keys whose change should trigger an update of this doc.
- `stage`: `planning` (build-plan only), `complete` (default), or `any`.
- `depends_on`: chapters to cross-link. Inside a pack, link as `[Architecture](#ch-architecture)`.
  A chapter in another pack is named in plain text, because that pack may have no PDF.

## Drafting a pack

1. Pack front matter: `title` (pack title from `packs`), `subtitle` (project name), `version: 1.0.0`,
   `date: YYYY-MM-DD`, `author` (from inputs, or git's top contributor if the user agrees, else
   `⟨assumption⟩`), `project`, `pack`, `chapters` (included ids, catalog order), and
   `confidential` if the user asked for it. Template front matter is not copied.
2. Each chapter opens with `# <Title> {#ch-<id>}` and keeps the template's `##` section order.
   Drop the template's "Related documents" and "Assumptions and open questions" sections; the pack
   has one assumptions chapter at the end. Delete sections that truly don't apply
   (e.g. "Database" for a static site) and say so in one line instead of leaving them empty.
3. Replace each `{{placeholder}}` with evidence-backed content. Placeholders the repo and
   inputs can't fill become `⟨assumption⟩` values or open questions. Never leave a raw `{{…}}` behind.
4. Keep diagrams in Mermaid (` ```mermaid `).
5. Finish the pack with the assumptions chapter (see writing-standards.md §2).

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

- Render only when the user asks, and only the packs they name.
- `build_pdf.py` options: `--theme`, `--out`, `--renderer weasyprint|chromium`, `--page-size a4|letter`,
  `--combine`, `--no-cover`, `--no-toc`. In a pack, each `#` chapter starts a page and the contents
  lists chapters with their `##` sections. It prints JSON (`{"outputs": [...], "renderer": ..., "warnings": [...]}`).
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
  {"pack": "developer", "hand_edited": false, "needs_patch": true, "chapters": [
    {"chapter": "api-reference", "included": true, "keys": ["routes"],
     "summary": ["route PATCH /orders/{order_id} added"]},
    {"chapter": "integration-guide", "included": false, "keys": ["routes"],
     "summary": ["route PATCH /orders/{order_id} added"]}]},
  {"pack": "ops", "hand_edited": true, "needs_patch": false, "chapters": []}],
 "unchanged": 1, "missing_markdown": [], "untracked": []}
```

- `included: true`: find that chapter's sections that cover the changed facts and edit them in place.
- `included: false`: a chapter left out of the pack now has evidence. Offer to add it; don't add it unasked.
- After patching: `state.py bump <pack>` (x.y.z → x.y.(z+1), date → today), then
  `state.py record --pack <pack>`. Re-render only if that pack already has a PDF.
- `hand_edited: true`: the user changed the Markdown since it was generated. Keep their text.
  If it also needs a patch, show the patch as a diff and wait for approval.
  If it only has hand edits and a PDF exists, re-render it (their edits should reach the PDF) and record it.
- `untracked`: a pack file in `docs/` that the skill didn't record. Leave it alone unless asked.
- `stage_suggestion`: the project gained code since the build plan, so ask whether it's complete.
