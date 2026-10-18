# Theme detection

`scripts/detect_theme.py <project> --out theme.json` reads a project's visual identity so the
PDFs look like they belong to it. Every resolved value records its `source` (file path or
`derived`/`default`) and a `confidence` (`high`, `medium` or `low`), so you can show the user
where it came from.

## Where it looks, in priority order

| Priority | Source | What it reads | Confidence |
|---|---|---|---|
| 1 | Tailwind v4 CSS `@theme { --color-*: … }` | color + font tokens | high |
| 1 | `tailwind.config.{js,ts,cjs,mjs}` `theme.extend.colors` / `fontFamily` | named colors | high |
| 2 | shadcn `globals.css` (`--primary`, `--background`, HSL/OKLCH triplets) | semantic roles | high |
| 2 | CSS/SCSS `:root { --primary… }`, `$primary:` | semantic roles | medium–high |
| 3 | MUI `createTheme`, Chakra `extendTheme`, Mantine `createTheme`, AntD `token.colorPrimary`, `theme.ts/js` | palette objects | medium |
| 3 | Flutter `ThemeData` / `ColorScheme.fromSeed` / `Color(0xFF…)` | primary/secondary/seed | medium |
| 3 | Android `res/values/colors.xml`, `themes.xml` (`colorPrimary`) | roles | medium |
| 3 | iOS `*.xcassets/*.colorset/Contents.json`, `extension Color` | named colors | medium |
| 3 | React Native `theme.(ts|js)`, `colors.(ts|js)` | palette objects | medium |
| 4 | Logo (`logo.*`, `favicon.*`, `icon.*` in `public/`, `assets/`, `static/`, `src/`) | file + dominant colour (Pillow) | low |
| – | Fonts: `@font-face`, Google Fonts `<link>`/`@import`, `font-family`, `next/font/google` imports, Tailwind `fontFamily` | heading/body/mono | medium |

Name matching for roles: `primary|brand|main` → primary; `secondary` → secondary;
`accent|highlight` → accent; `background|bg` → bg; `surface|card|paper` → surface;
`foreground|text` → text; `muted|subtle` → muted; `border|divider|outline` → border;
`success|green` / `warning|amber|yellow` / `danger|error|destructive|red` → status colours.

## Normalisation

1. Parse hex, `rgb()`, `hsl()`, shadcn bare HSL triplets (`222 47% 11%`), `oklch()`
   (approximate conversion) and Flutter `0xAARRGGBB`. Convert everything to `#rrggbb`.
2. Fill missing roles from what exists:
   - `secondary` = primary rotated toward its complement and darkened; `accent` = a hue shift of primary.
   - `surface` = bg mixed 4% toward primary; `border` = text mixed 85% toward bg.
   - `muted` = text mixed 45% toward bg; status colours use safe defaults.
3. **Dark-mode-only projects** (bg luminance < 0.2): print needs a light page, so swap to a
   light variant. bg = `#ffffff`, text = the darkest palette colour or `#111827`, and brand
   colours are kept. Set `dark_mode_mapped: true` and tell the user.
4. **WCAG contrast:** require 4.5:1 for `text` on `bg` and on `surface`, `primary` on white
   (used for headings and links), and `muted` on `bg` (3:1 allowed; it's only for captions).
   If a pair fails, darken the foreground in small lightness steps until it passes. Record the
   original in `adjustments[]`, so the brand colour stays recognisable but stays readable.
   If a fix shifts lightness by more than 30%, flag it instead of fixing silently.

## Fonts

Detected font names are matched against the bundled fonts in `assets/fonts/`:

| Bundled | Covers |
|---|---|
| Inter | sans UI fonts (Inter, Geist, SF, Roboto, Helvetica, Arial, Open Sans, Lato, Poppins, system-ui) |
| Source Serif 4 | serifs (Georgia, Merriweather, Lora, Times, PT Serif) |
| Fraunces | display/headline serifs (Playfair, DM Serif, Recoleta) |
| JetBrains Mono | monospace (Fira Code, Menlo, SF Mono, Consolas, Source Code Pro) |

If a detected font is neither bundled nor installed locally, the closest bundled font is
used and `fonts.substitutions[]` records the swap. Always tell the user about the swap.

## theme.json schema (shared with `themes/*.json`)

```json
{
  "name": "acme-detected",
  "label": "Acme (detected)",
  "colors": {"primary": "#…", "secondary": "#…", "accent": "#…", "bg": "#…", "surface": "#…",
             "text": "#…", "muted": "#…", "border": "#…", "success": "#…", "warning": "#…", "danger": "#…"},
  "cover": {"bg": "#…", "text": "#…"},
  "fonts": {"heading": "Inter", "body": "Inter", "mono": "JetBrains Mono"},
  "logo": "public/logo.svg",
  "meta": {"sources": {"primary": {"source": "tailwind.config.ts", "confidence": "high"}},
           "adjustments": [], "dark_mode_mapped": false, "substitutions": []}
}
```

`logo` is relative to the project root (the folder containing `docs/`), or `null`.
Ties between equally confident sources go to the app's own theme code: Android/iOS resource
colours rank below Dart/JS themes, because in Flutter/React Native apps they are usually
launcher or splash colours. When a brand colour fails contrast, a darker shade the project
already defines (e.g. `brand-700`) is preferred over a computed one.

`cover` is optional. It defaults to `primary` bg with white text, and `midnight` uses it for a dark cover.
