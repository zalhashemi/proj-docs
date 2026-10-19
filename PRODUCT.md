# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users
Mixed readers of generated project documentation. Engineers use the Developer and Ops packs as working reference (commands, tables, code). Managers, clients and incoming owners read the Business and Handover packs, which are shared as PDF attachments.

## Product Purpose
`project-docs` is a Claude Code skill that turns a real repository into one evidence-based Markdown pack per category (Planning, Developer, Business, User, Ops, Handover and Governance). It renders a branded PDF only when asked. Success means the docs can be trusted, because verified facts and assumptions are visibly separated, and they read well enough to hand to a stakeholder unchanged.

## Positioning
Every claim is grounded in the repo, cites a path, or is visibly marked as an assumption. Packs are patched, never rewritten, when the code changes.

## Operating Context
PDFs are read mostly on screen, in a PDF viewer or browser. They are rendered by WeasyPrint or headless Chromium from Markdown via `skills/project-docs/scripts/build_pdf.py` and `assets/base.css`, at A4 or US Letter.

## Capabilities and Constraints
- Every colour and font comes from a theme (`themes/*.json` or a theme detected from the project's UI). The default look has to hold up when a detected brand's colours, fonts and logo replace its own.
- Fonts: only the bundled OFL faces (Fraunces, Source Serif 4, Inter, JetBrains Mono). No new font downloads.
- Content has fixed elements: a cover, contents, chapters (`#`) with sections (`##`), tables (including key/value tables and Gantt tables), code blocks, Mermaid diagrams, charts, and callouts (note, tip, warning, important, assumption), plus inline tags for assumption and untested.
- `verify_pdf.py` enforces contrast of at least 4.5:1, no text outside the margins, embedded fonts, and working TOC links.

## Brand Commitments
Assumptions must be spotted at a glance. Sample themes ship as alternatives: clean-light, corporate-blue, midnight, warm-editorial, mono-minimal.

## Evidence on Hand
Samples in `samples/brightcart` (React SPA) and `samples/ledgerline` (FastAPI service). Dogfooded docs are in `docs/`. There are no customer testimonials or usage numbers, and none may be invented.

## Product Principles
- Trust first: fact versus assumption is always visible.
- Generate only what was asked for.
- Patch, don't rewrite.
- Brand-neutral by default, brand-faithful when detected.
