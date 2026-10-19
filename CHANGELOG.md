# Changelog

## 2.0.0 (2026-10-19)

**Breaking:** per-document files are no longer generated. Existing `docs/<id>.md` files and the
old `state.json` format aren't migrated; re-run the skill to write packs.

- **One Markdown pack per category.** Each run writes one `docs/<pack>.md` per pack you pick
  (Planning, Developer, Business, User, Ops, Handover and Governance). Each of the 37 doc types
  is a chapter of exactly one pack (catalog `pack`); `presets` are replaced by `packs`.
- **Chapters need evidence.** A new catalog field `needs` and `state.py packs` leave out chapters
  the repo can't back up, such as a data model with no database. Each pack ends with one
  assumptions chapter that says what was left out and why.
- **PDFs only on request**, one per named pack (`docs/pdf/<pack>.pdf`). `--combine` remains for an
  explicit all-packs PDF.
- **Pack-level update tracking.** `state.py record/diff/bump` work per pack; `diff` names the
  affected chapters and offers left-out chapters that now have evidence. A PDF is re-rendered only
  if one already exists.
- **New default look, "Spectrum"** (`themes/default.json`), designed with the impeccable and
  design-taste skills: one colour per pack, a full-bleed chapter band with the chapter number,
  title and pack on every chapter page, numbered contents, open tables, flat callouts with square
  label plates. Brand themes still replace colours, fonts and logo. The design system is
  documented in `DESIGN.md`.
- `verify_pdf.py` checks white-on-pack-colour contrast; doubled Chromium bookmarks are fixed.
- Samples and the dogfooded guide are regenerated as packs.

## 1.0.0 (2026-10-18)

First public release.

- 37 document types in 6 presets (Developer, Business, User, Ops, Handover, Everything), plus a
  pre-build `build-plan`.
- Theme detection from Tailwind (v3/v4), CSS variables/shadcn, MUI/Chakra/Mantine/AntD,
  Flutter, Android, iOS and React Native, with logo colour fallback and WCAG contrast fixes.
- 5 default themes and a theme preview sheet.
- PDF rendering with WeasyPrint or Chromium: cover, TOC with page numbers, running
  header/footer, callouts, highlighted code, branded Mermaid diagrams, combined docs pack.
- `finance.py` for forecast and budget maths; `verify_pdf.py` for automated checks and thumbnails.
- Update mode: `state.py diff` flags only the documents whose source facts changed and
  detects hand edits.
- `bootstrap.py` sets up dependencies on first use (asks before installing).
