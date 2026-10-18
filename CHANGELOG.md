# Changelog

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
