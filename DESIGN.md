---
name: project-docs
description: The default look of project-docs PDF packs. One flat colour per pack, a full-bleed chapter band, a calm serif reading column.
colors:
  pack-planning: "#4f5d6b"
  pack-developer: "#0068a8"
  pack-business: "#00775a"
  pack-user: "#b45200"
  pack-ops: "#1e4f8f"
  pack-handover: "#566b1f"
  ink: "#17191c"
  muted: "#5f6670"
  paper: "#ffffff"
  surface: "#f3f4f5"
  hairline: "#dfe2e5"
  assumption-amber: "#8a5a00"
  danger: "#b3261e"
  success: "#00775a"
typography:
  cover-title:
    fontFamily: "Inter, sans-serif"
    fontSize: "46pt"
    fontWeight: 700
    lineHeight: 1
    letterSpacing: "-0.03em"
  band-number:
    fontFamily: "Inter, sans-serif"
    fontSize: "46pt"
    fontWeight: 700
    letterSpacing: "-0.04em"
  chapter-title:
    fontFamily: "Inter, sans-serif"
    fontSize: "30pt"
    fontWeight: 700
    lineHeight: 1.05
    letterSpacing: "-0.03em"
  section:
    fontFamily: "Inter, sans-serif"
    fontSize: "15pt"
    fontWeight: 700
    letterSpacing: "-0.015em"
  body:
    fontFamily: "Source Serif 4, serif"
    fontSize: "10pt"
    fontWeight: 400
    lineHeight: 1.55
  table:
    fontFamily: "Inter, sans-serif"
    fontSize: "8.4pt"
    lineHeight: 1.4
  code:
    fontFamily: "JetBrains Mono, monospace"
    fontSize: "8.1pt"
    lineHeight: 1.5
rounded:
  none: "0"
spacing:
  page-top: "22mm"
  page-side: "18mm"
  page-bottom: "20mm"
  band: "58mm"
components:
  chapter-band:
    backgroundColor: "{colors.pack-developer}"
    textColor: "{colors.paper}"
    width: "{spacing.band}"
  chapter-lead:
    backgroundColor: "#e6f0f6"
    textColor: "{colors.ink}"
    padding: "4.5mm 5mm"
  callout-label:
    backgroundColor: "{colors.pack-developer}"
    textColor: "{colors.paper}"
    rounded: "{rounded.none}"
    padding: "0.6mm 2mm"
  code-block:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.code}"
    rounded: "{rounded.none}"
    padding: "3.5mm 4mm"
---

# Design System: project-docs

## Overview

**Creative North Star: "The Spectrum Index"**

After Otl Aicher's identity for the 1972 Munich Olympics. Each pack owns one flat colour from a cool spectrum, and colour plus a fixed grid do the wayfinding: a reader knows which pack they hold from across the room and which chapter they're in from the band on every page. The frame is bold and the reading column stays quiet: flat colour fields, sharp corners, no shadows, a serif column at a real measure.

Brand themes detected from a project's UI replace the colours, fonts and logo. Every pack then takes the brand primary, and the cover strip uses tints of it. The structure stays.

**Key Characteristics:**
- One colour per pack, used for the cover field, the chapter band, section markers, table heads and links.
- A full-bleed band down the left of every chapter page, holding the chapter number, title, pack and project.
- Inter frame, Source Serif 4 reading column, JetBrains Mono for code only.
- All corners square. No shadows, gradients or rules heavier than 1.4pt.

## Colors

A cool spectrum of six deep tones, every one at 5:1 or better against white, on a white page with near-black ink.

### Primary
- **Developer Blue** (#0068a8), **Business Green** (#00775a), **User Orange** (#b45200), **Ops Navy** (#1e4f8f), **Handover Olive** (#566b1f), **Planning Slate** (#4f5d6b): one per pack, exposed as `--pack`. Its 10% tint (`--pack-tint`) is the only field colour in the reading column.

### Neutral
- **Ink** (#17191c): all running text and headings.
- **Muted** (#5f6670): running footer, contents sub-entries, captions.
- **Surface** (#f3f4f5): code blocks and inline code.
- **Hairline** (#dfe2e5): table row rules.

### Named Rules
**The One Pack Colour Rule.** A pack PDF uses only its own pack colour plus the status colours (amber, red, green) for callouts. The other pack colours appear only in the cover strip.
**The Amber Means Unverified Rule.** The assumption amber marks assumptions and nothing else, always with a dashed frame, so the mark survives greyscale.

## Typography

**Display Font:** Inter (with sans-serif)
**Body Font:** Source Serif 4 (with Inter, sans-serif)
**Mono Font:** JetBrains Mono

**Character:** A neutral grotesk carries the frame and every label; a sturdy text serif carries the reading. The bundled-fonts constraint pins this set, and Inter stands in for Aicher's Univers.

### Hierarchy
- **Cover title** (700, 46pt, 1.0): the pack name on the cover field.
- **Band number** (700, 46pt): the chapter number at the top of the band.
- **Chapter title** (700, 30pt, 1.05): the `#` heading at the top of the column.
- **Section** (700, 15pt): `##` headings, led by a 2.6mm pack-colour square.
- **Body** (400, 10pt, 1.55): Source Serif 4 in a 134mm column.
- **Table** (8.4pt Inter): header in the pack colour over a 1.4pt pack-colour rule.

## Layout

A4 or US Letter. Cover and contents use 22/18/20mm margins. Chapter pages widen the left margin to 58mm and paint it as the pack band, drawn with page margin boxes (page content is clipped to its box in Chromium, so it cannot bleed). Each chapter starts a page. Sections are separated by space (10mm above a section heading), not rules.

## Elevation & Depth

Flat. Depth comes from colour fields only: the band, the lead tint, callout tints. No shadows anywhere.

## Shapes

Every corner is square: code blocks, callouts, label plates, chips and position marks.

## Components

- **Chapter band:** the pack colour, full height, left edge. Number at the top, title at the upper middle, pack and project at the bottom.
- **Chapter lead:** the first paragraph of a chapter, on the pack tint, at 11pt.
- **Callouts:** a flat tint field with a square label plate whose colour and word carry the kind (Note, Tip, Important, Warning). Assumptions add a dashed amber frame over a light hatch.
- **Tables:** no fill, no vertical rules; pack-colour header text over a 1.4pt rule, hairline rows. Key/value tables sit on the pack tint with pack-colour keys.
- **Cover:** the pack colour over the top 58%, the pack name bottom-left in white; under it the six-colour spectrum strip with this pack's segment dropped lower; project name and a version/chapters/date/author table on white.
- **Contents:** chapters numbered 01, 02 in the pack colour, sections indented beneath them.

## Do's and Don'ts

- Do keep text 10mm or more from the page edge, because `verify_pdf.py` fails anything within 6mm.
- Do derive every pack colour so white text on it reaches 4.5:1.
- Don't add a coloured border-left to callouts or any other block; the band is the only vertical colour.
- Don't put labels or kickers above headings; headings carry themselves.
- Don't use the em-dash in generated text.
