# project-docs

A Claude Code skill that turns a repository into project documentation: one Markdown pack per
category you pick (Planning, Developer, Business, User, Ops, Handover and Governance), made of
37 chapter types, and a branded PDF of a pack when you ask for one. It writes the Planning pack
before the project exists and the others once it's complete. PDFs use the project's own colours,
fonts and logo, or the default Spectrum theme. When the code changes, it patches only the
affected chapter sections and re-renders only packs that already have a PDF.

Ask Claude things like *"generate a docs pack for this project"*, *"write a runbook"*,
*"make a 1-year forecast and budget"*, or *"update the docs"*.

## Install

### As a Claude Code plugin (recommended)

```text
/plugin marketplace add zalhashemi/proj-docs
/plugin install project-docs@proj-docs
```

### Manually

```bash
git clone https://github.com/zalhashemi/proj-docs.git
cp -R proj-docs/skills/project-docs ~/.claude/skills/          # all projects
# or: cp -R proj-docs/skills/project-docs <your-repo>/.claude/skills/   (one project)
```

### Dependencies

You don't need to install anything up front. On first use, the skill runs
`scripts/bootstrap.py`. If packages are missing, Claude asks before running
`bootstrap.py --install`, which creates a venv in `~/.cache/project-docs/venv` and installs
`requirements.txt`. To do it yourself:

```bash
python3 skills/project-docs/scripts/bootstrap.py --install    # add --with-chromium if needed
```

| Need | What | Install |
|---|---|---|
| Required | Python 3.9+ | python.org or your package manager |
| One renderer | **WeasyPrint** (default) needs Pango | macOS: `brew install pango` · Debian/Ubuntu: `sudo apt install libpango-1.0-0 libpangoft2-1.0-0` · Windows: GTK3 runtime ([WeasyPrint docs](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html)) |
| | or **Chromium** | an installed Google Chrome/Edge, or `bootstrap.py --install --with-chromium` (about 150 MB, needs network once) |
| Optional | `mmdc` renders Mermaid diagrams in the theme's colours | `npm i -g @mermaid-js/mermaid-cli`. Without it, diagrams show as source with a note |
| Optional | `pdftoppm` (poppler) for thumbnails | PyMuPDF is used when it's missing |

If the chosen renderer is missing, `build_pdf.py` switches to the other one and says why.
Nothing needs network access at runtime. Override the environment with `PROJECT_DOCS_PYTHON`
(an interpreter) or `PROJECT_DOCS_VENV` (where `--install` puts the venv).

## How it works

```text
scan_project.py ─► scan.json ─┐
detect_theme.py ─► theme.json ├─► Claude drafts docs/<pack>.md from templates/ ─► state.py record ─► state.json
inputs.yaml (your answers) ───┘        (finance.py does all the maths)
                                    on request: build_pdf.py ─► docs/pdf/<pack>.pdf ─► verify_pdf.py ─► previews
```

| File | Role |
|---|---|
| `SKILL.md` | Trigger description and the workflow Claude follows (kept under 150 lines) |
| `catalog.yaml` | Packs, and every chapter type: its pack, sources, questions, template, `needs`, `scan_keys` |
| `templates/*.md` | One outline per chapter type, with `<!-- guide: -->` notes for the drafter |
| `reference/` | Writing standards (no fabrication, assumption rules), theme detection, workflow details |
| `themes/*.json` | `default` (Spectrum: one colour per pack), plus clean-light, midnight, corporate-blue, warm-editorial, mono-minimal |
| `assets/` | `base.css` (print styles driven by CSS variables), `cover.html.j2`, bundled OFL fonts. The design rules are in the repo's `DESIGN.md` |
| `scripts/` | The tools below; each has `--help` and prints JSON |

Output stays inside the target project:

- `docs/<pack>.md`: one per selected pack, the source of truth, which you can edit
- `docs/pdf/<pack>.pdf`: only for packs you asked to render
- `docs/.project-docs/`: scan, theme, inputs, state, charts and previews

## Script usage

```bash
S=skills/project-docs/scripts                     # or wherever the skill is installed
PY=$(python3 $S/bootstrap.py | python3 -c "import json,sys; print(json.load(sys.stdin)['python'])")

$PY $S/scan_project.py .                               # -> docs/.project-docs/scan.json
$PY $S/detect_theme.py .                               # -> docs/.project-docs/theme.json
$PY $S/detect_theme.py . --use midnight                # pick a bundled theme instead
$PY $S/state.py packs                                  # chapters per pack the scan supports, and those skipped
$PY $S/preview_themes.py                               # one swatch page per theme
$PY $S/finance.py forecast --inputs docs/.project-docs/inputs.yaml --theme docs/.project-docs/theme.json
$PY $S/build_pdf.py docs/developer.md                  # -> docs/pdf/developer.pdf
$PY $S/build_pdf.py docs/*.md --combine                # -> docs/pdf/docs-pack.pdf (all packs, on request)
$PY $S/build_pdf.py docs/*.md --renderer chromium --page-size letter
$PY $S/verify_pdf.py docs/pdf/*.pdf --theme docs/.project-docs/theme.json
$PY $S/state.py set-stage complete                     # lifecycle: planning -> complete
$PY $S/state.py record                                 # remember what each pack was built from
$PY $S/state.py diff                                   # what changed since, per pack and chapter
$PY $S/state.py bump developer                         # version 1.0.0 -> 1.0.1, date -> today
```

Use `--exclude 'path/*'` on `scan_project.py` and `detect_theme.py` to skip sample or fixture
folders.

## Add a chapter type

1. Add an entry to `catalog.yaml`. Every field is required except `stage` and `needs`:

   ```yaml
   - id: accessibility-report
     title: Accessibility Report
     audience: governance            # planning|business|developer|ops|user|governance
     pack: user                      # the one pack it's a chapter of (see `packs`)
     description: "WCAG 2.2 AA checklist with findings from the repo."
     sources_to_scan: ["src/**/*.tsx", ".eslintrc*"]
     required_inputs:
       - {key: wcag_level, question: "Target level?", type: choice, choices: [A, AA, AAA], default: AA}
     template: accessibility-report.md
     est_pages: "2-4"
     requires_ui: true               # then the template needs a <!-- variant: cli-api --> section
     depends_on: [user-guide]
     scan_keys: [has_ui, frameworks] # changes here flag the chapter in update mode
     needs: [has_ui]                 # optional: skip the chapter unless one of these has evidence
   ```

2. Create `templates/accessibility-report.md`:
   - front matter whose `doc_id` and `title` match the catalog entry
   - `<!-- guide: -->` comments for each section
   - `{{placeholders}}`
   - an `## Assumptions and open questions` section (merged into the pack's last chapter)

3. Run `pytest tests/test_catalog.py` (from the repository root). It checks the schema, the template, the
   cross-links and that each shared input key has a consistent type.

## Add a theme

Copy `themes/default.json` to `themes/<name>.json` and change `name`, `label`, `colors`
(all 11 roles) and `fonts`. Keep `packs` (one colour per pack id) or delete it, and every pack
uses the primary colour. Add `cover: {bg, text}` for a cover that isn't the pack colour.
Use bundled font names (Inter, Source Serif 4, Fraunces, JetBrains Mono) or fonts installed on
the machine. The catalog tests enforce WCAG contrast: text on bg/surface and primary on white
must be at least 4.5:1, white on each pack colour at least 4.5:1, and muted on bg at least 3:1. Check the result with `preview_themes.py`.

## Tests

From the repository root:

```bash
~/.cache/project-docs/venv/bin/python -m pytest tests -q
```

The suite covers the catalog and templates, the scanner and theme detection on three fixtures
(React + Tailwind, FastAPI, Flutter) plus edge cases, rendering, verification, finance maths,
pack update tracking, and a full end-to-end build of 3 packs per fixture.
Rendering tests skip themselves when no renderer is installed.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `WeasyPrint unavailable (cannot load library 'libgobject-2.0-0'…)` | Install Pango (see Dependencies) or ignore it: Chromium is used automatically |
| `no PDF renderer available` | Install Pango, run `bootstrap.py --install --with-chromium`, or install Google Chrome |
| Diagrams appear as code | Install `mmdc` (mermaid-cli); on Linux containers it runs with `--no-sandbox` automatically |
| Text overflows a table (verify reports "outside the margins") | Use fewer columns (6 or fewer), shorter cells, and wrap long tokens in backticks |
| Detected font replaced by Inter or Fraunces | The font isn't bundled or installed. Install it locally or accept the substitute |
| Logo missing from the cover | `theme.json` → `logo` is relative to the project root; check that the file exists |
| Fixture or sample colours mixed into the theme | Re-run with `--exclude 'path/to/fixtures/*'` |
| `all Markdown inputs must be in the same docs/ folder` | Build each project's docs in its own call |
| `bootstrap.py` reports missing packages | Run `bootstrap.py --install` (asks no questions; needs network) |

## Known limitations

- Route detection uses regular expressions (best effort). Each route records a confidence level.
- Chromium can't compute TOC page numbers, so it renders twice and reads the page numbers from
  the first pass. If the links found don't match the TOC entries, the numbers are left out and
  `build_pdf.py` prints a "TOC page numbers skipped" warning.
- Charts use matplotlib's default font, because matplotlib can't load the bundled `.woff2` files.
- The bundled fonts cover Latin characters only. Other scripts fall back to system fonts.
- Dependency licences are read only from locally installed packages, and "outdated" checks
  need the network, so they're reported as "not checked".
