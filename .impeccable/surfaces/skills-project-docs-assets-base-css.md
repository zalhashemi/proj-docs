---
version: 1
slug: "skills-project-docs-assets-base-css"
primary_target: "skills/project-docs/assets/base.css"
related_targets: ["skills/project-docs/assets/cover.html.j2"]
---

# Surface: default PDF look (project-docs packs)

Scope: assets/base.css, assets/cover.html.j2, themes/default.json, build_pdf.py page CSS. Mode: Read.
Audience: engineers (Developer/Ops packs) and stakeholders (Business/Handover), read on screen.
Constraints: bundled fonts only (Inter, Source Serif 4, JetBrains Mono; Fraunces not used); brand themes replace colours, fonts, logo; WeasyPrint + Chromium; verify_pdf contrast 4.5:1.

## Direction contract

THESIS: Munich '72 Spectrum. Each pack owns one flat colour from a cool spectrum; flat colour fields and a rigid grid do the wayfinding. Refuses the SaaS-docs default of blue header bars, zebra tables and left-border callouts.

OWN-WORLD: White page, off-black ink #17191c, one pack colour per document (planning slate, developer blue, business green, user orange, ops dark blue, handover olive), its 10% tint as the only field colour. All corners sharp. Inter for frame and headings, Source Serif 4 for running text, JetBrains Mono for code. Small solid squares as section markers; a spectrum strip of all six pack colours with the current one tall.

STORY: The reader knows which pack they hold from colour alone, finds a chapter by its number and edge tab, reads a calm serif column, and spots assumptions by their dashed amber frame.

FIRST VIEWPORT: Chapter opener page: a full-height pack-colour column (about 62mm) bleeding off the left edge, holding the two-digit chapter number at about 64pt, the chapter title in white Inter Bold, the pack and project names, and a row of position squares (current one solid). Content starts beside it with the lead paragraph on a tint field. Following pages: a pack-colour edge tab in the right margin, stepped by chapter. Cover: pack-colour field over the top 60% with the pack title in large white Inter Bold and the spectrum strip; project, version, date and author below on white.

FORM: Munich '72 Spectrum (Otl Aicher Olympic identity), my rank 1 of 7, chosen as IMPECCABLE'S PICK over the roll; seed key 2beb7328.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
