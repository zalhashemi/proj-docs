#!/usr/bin/env python3
"""Detect a project's visual identity (colours, fonts, logo) and write a print-safe theme.json.

Each resolved value records its source file and a confidence level. Missing roles are derived
from the primary colour, WCAG contrast is enforced, and dark-only palettes are mapped to a
light print variant. With no usable UI signals, the --default theme is written instead.

Usage:
  detect_theme.py <project> [--out PATH] [--default clean-light]
  detect_theme.py <project> --use midnight      # just write a bundled default theme
See reference/theme-detection.md for the rules.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter
from functools import lru_cache
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import (SKILL_DIR, contrast, ensure_contrast, lightness, load_json, luminance,  # noqa: E402
                     mix, parse_color, read_text, rgb_to_hex, saturation, shift, write_json)
from scan_project import Scanner  # noqa: E402

ROLES = ["primary", "secondary", "accent", "bg", "surface", "text", "muted", "border",
         "success", "warning", "danger"]
# Checked in this order so "text-primary" maps to text before primary gets a chance.
ROLE_PATTERNS = [
    ("muted", r"muted-?foreground|text-?(secondary|muted|subtle)|muted-?text|colortextsecondary|subtle|subtext|onsurfacevariant"),
    ("text", r"foreground|text|textcolor|text-?primary|colortext(base)?|on-?background|on-?surface|ink|body-?text"),
    ("bg", r"background|bg|backgroundcolor|colorbgbase|canvas|scaffoldbackgroundcolor|page"),
    ("surface", r"surface|card|paper|background-?paper|popover|colorbgcontainer|surface-?container"),
    ("border", r"border|divider|outline|colorborder|input|stroke"),
    ("primary", r"primary|brand|main|colorprimary|primarycolor|brand-?primary|seed|seedcolor|colorschemeseed"),
    ("secondary", r"secondary|colorsecondary|secondarycolor|brand-?secondary"),
    ("accent", r"accent|coloraccent|accentcolor|highlight|tertiary"),
    ("success", r"success|colorsuccess|positive"),
    ("warning", r"warning|colorwarning|caution"),
    ("danger", r"danger|error|destructive|colorerror|negative"),
]
ROLE_RX = [(r, re.compile(rf"(?:{p})")) for r, p in ROLE_PATTERNS]
GENERIC_SEGMENTS = {"theme", "extend", "colors", "color", "palette", "light", "tokens", "token",
                    "semantic", "sys", "ref", "app", "scheme", "colorscheme", "default"}
SHADE_PREF = {None: 0, "default": 0, "main": 0, "base": 0, "600": 1, "500": 2, "700": 3}
CONF_RANK = {"high": 0, "medium": 1, "low": 2}
DEFAULTS = {"bg": "#ffffff", "text": "#111827", "success": "#15803d", "warning": "#b45309",
            "danger": "#b91c1c"}

BUNDLED = {"Inter": "sans", "Source Serif 4": "serif", "Fraunces": "display", "JetBrains Mono": "mono"}
CATEGORY_FONT = {"sans": "Inter", "serif": "Source Serif 4", "display": "Fraunces", "mono": "JetBrains Mono"}
GENERIC_FONTS = {"sans-serif", "serif", "monospace", "system-ui", "ui-sans-serif", "ui-serif",
                 "ui-monospace", "-apple-system", "blinkmacsystemfont", "inherit", "initial",
                 "cursive", "fantasy", "emoji", "math", "apple color emoji", "segoe ui emoji"}


# ---------------------------------------------------------------- name -> role

def role_of(name: str) -> tuple[str | None, str | None, bool]:
    """Map a token name to (role, shade, is_dark)."""
    n = re.sub(r"([a-z])([A-Z])", r"\1-\2", name).lower()
    n = re.sub(r"[^a-z0-9]+", "-", n).strip("-")
    segs = [s for s in n.split("-") if s]
    dark = "dark" in segs or "night" in segs
    segs = [s for s in segs if s not in ("dark", "night")]
    while segs and segs[0] in GENERIC_SEGMENTS and len(segs) > 1:
        segs.pop(0)
    shade = None
    if len(segs) > 1 and (segs[-1].isdigit() or segs[-1] in ("default", "main", "base")):
        shade = segs.pop()
    key = "-".join(segs)
    for role, rx in ROLE_RX:
        if rx.fullmatch(key) or rx.fullmatch(key.replace("-", "")):
            return role, shade, dark
    return None, shade, dark


# ---------------------------------------------------------------- extractors

def _cand(out, name, value, source, conf, prio, dark=False):
    hexv = parse_color(value) if isinstance(value, str) else value
    if not hexv:
        return
    role, shade, name_dark = role_of(name)
    out.append({"name": name, "role": role, "shade": shade, "value": hexv, "source": source,
                "confidence": conf, "priority": prio, "dark": dark or name_dark})


def js_object_colors(text: str, source: str, conf: str, prio: int, out: list) -> None:
    """Walk nested `key: {` / `key: 'value'` pairs in JS/TS objects (Tailwind, MUI, Chakra, RN)."""
    stack: list[str | None] = []
    rx = re.compile(r"""(['"]?)([\w$-]+)\1\s*:\s*(\{|'[^'\n]*'|"[^"\n]*"|`[^`\n]*`)|(\{)|(\})""")
    for m in rx.finditer(text):
        if m.group(5):
            if stack:
                stack.pop()
        elif m.group(4):
            stack.append(None)
        elif m.group(3) == "{":
            stack.append(m.group(2))
        else:
            name = "-".join([k for k in stack if k] + [m.group(2)])
            _cand(out, name, m.group(3)[1:-1], source, conf, prio)


def css_colors(text: str, source: str, out: list, fonts: list) -> None:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    variables: dict[str, str] = {}
    stack: list[str] = []
    last = 0
    for m in re.finditer(r"[{};]", text):
        chunk = text[last:m.start()].strip()
        last = m.end()
        if m.group() == "{":
            stack.append(chunk)
            continue
        if m.group() == "}":
            if chunk:  # declaration without trailing semicolon
                _css_decl(chunk, stack, variables, source, out, fonts)
            if stack:
                stack.pop()
            continue
        _css_decl(chunk, stack, variables, source, out, fonts)


def _css_decl(decl, stack, variables, source, out, fonts):
    if ":" not in decl:
        return
    prop, value = (s.strip() for s in decl.split(":", 1))
    ctx = " ".join(stack).lower()
    dark = ".dark" in ctx or "dark" in ctx and ("data-theme" in ctx or "prefers-color-scheme" in ctx)
    value = re.sub(r"var\((--[\w-]+)[^)]*\)", lambda v: variables.get(v.group(1), v.group(0)), value)
    if prop.startswith(("--", "$")):
        name = prop.lstrip("-$")
        variables[prop] = value
        if name.startswith("font-") or name.startswith("font_"):
            role = {"sans": "body", "body": "body", "serif": "body", "heading": "heading",
                    "display": "heading", "title": "heading", "mono": "mono", "code": "mono"}.get(
                name.split("-", 1)[1].split("-")[0])
            if role:
                fonts.append({"role": role, "family": value, "source": source, "confidence": "high"})
            return
        is_theme = "@theme" in ctx or ":root" in ctx or ".dark" in ctx or not stack or prop.startswith("$")
        _cand(out, name, value, source, "high" if is_theme else "medium", 2 if "@theme" not in ctx else 1, dark)
    elif prop == "font-family":
        sel = stack[-1].lower() if stack else ""
        if "@font-face" in sel:
            fonts.append({"role": None, "family": value, "source": source, "confidence": "medium"})
        elif re.search(r"\bh[1-6]\b|heading|title|display", sel):
            fonts.append({"role": "heading", "family": value, "source": source, "confidence": "medium"})
        elif re.search(r"\b(code|pre|kbd)\b", sel):
            fonts.append({"role": "mono", "family": value, "source": source, "confidence": "medium"})
        elif re.search(r"\b(body|html)\b|:root", sel):
            fonts.append({"role": "body", "family": value, "source": source, "confidence": "medium"})
    elif prop in ("color", "background", "background-color") and stack and \
            re.search(r"\b(body|html)\b|:root", stack[-1].lower()):
        _cand(out, "text" if prop == "color" else "background", value, source, "medium", 2, dark)


def tailwind_fonts(text: str, source: str, fonts: list) -> None:
    block = re.search(r"fontFamily\s*:\s*\{(.*?)\n\s*\}", text, re.S)
    if not block:
        return
    for key, val in re.findall(r"(\w+)\s*:\s*\[([^\]]*)\]", block.group(1)):
        role = {"sans": "body", "body": "body", "serif": "body", "display": "heading",
                "heading": "heading", "title": "heading", "mono": "mono"}.get(key)
        if role:
            fonts.append({"role": role, "family": val, "source": source, "confidence": "high"})


def google_font_links(text: str, source: str, fonts: list) -> None:
    for url in re.findall(r"fonts\.googleapis\.com/css2?\?([^\"')\s>]+)", text):
        for fam in re.findall(r"family=([^:&]+)", url):
            fonts.append({"role": None, "family": fam.replace("+", " "), "source": source, "confidence": "medium"})
    for imp in re.findall(r"import\s*\{([^}]+)\}\s*from\s*['\"](?:next/font/google|@fontsource)[^'\"]*['\"]", text):
        for fam in imp.split(","):
            fam = fam.strip().split(" as ")[0].replace("_", " ")
            if fam:
                fonts.append({"role": None, "family": fam, "source": source, "confidence": "medium"})


def dart_colors(text: str, source: str, out: list, fonts: list) -> None:
    # Split by ThemeData so a dark ThemeData's colours are tagged dark.
    parts = re.split(r"(?=ThemeData\s*\()", text)
    for part in parts:
        dark = bool(re.search(r"Brightness\.dark", part[:600])) and part.startswith("ThemeData")
        for name, hexv in re.findall(r"(\w+)\s*:\s*(?:const\s+)?Color\(\s*0x([0-9A-Fa-f]{8})\s*\)", part):
            if name.startswith("on") and name not in ("onSurface", "onBackground"):
                continue
            _cand(out, name, "0x" + hexv, source, "medium", 3, dark)
        for name, hexv in re.findall(r"static\s+const\s+Color\s+(\w+)\s*=\s*Color\(\s*0x([0-9A-Fa-f]{8})", part):
            _cand(out, name, "0x" + hexv, source, "low", 3, dark)
    for fam in re.findall(r"fontFamily\s*:\s*['\"]([^'\"]+)['\"]", text):
        fonts.append({"role": "body", "family": fam, "source": source, "confidence": "medium"})
    for fam in re.findall(r"GoogleFonts\.(\w+?)(?:TextTheme)?\(", text):
        fonts.append({"role": "body", "family": re.sub(r"([a-z])([A-Z])", r"\1 \2", fam).title(),
                      "source": source, "confidence": "medium"})


# Native resources get priority 4: in Flutter/RN apps they are usually launcher/splash colours,
# so the Dart/JS theme wins ties. Pure native apps have nothing else, so they still resolve.
def android_colors(text: str, source: str, out: list, palette: dict) -> None:
    for name, val in re.findall(r"<color\s+name=\"([\w.]+)\"\s*>\s*(#[0-9A-Fa-f]{3,8})\s*<", text):
        val = "#" + val[-6:] if len(val) == 9 else val  # Android #AARRGGBB
        palette[name] = val
        _cand(out, name, val, source, "medium", 4, "values-night" in source)
    for name, val in re.findall(r"<item\s+name=\"(?:android:)?(\w+)\"\s*>\s*([@#][\w/]+)\s*<", text):
        val = palette.get(val.split("/")[-1], val) if val.startswith("@color/") else val
        _cand(out, name, val, source, "medium", 4, "values-night" in source)


def ios_colorset(path: Path, source: str, out: list) -> None:
    try:
        data = json.loads(read_text(path))
    except ValueError:
        return
    name = path.parent.name.replace(".colorset", "")
    for c in data.get("colors", []):
        comp = (c.get("color") or {}).get("components") or {}
        dark = any(a.get("value") == "dark" for a in c.get("appearances", []))
        try:
            rgb = []
            for k in ("red", "green", "blue"):
                v = str(comp[k])
                rgb.append(int(v, 16) if v.startswith("0x") else float(v) * 255 if "." in v or float(v) <= 1 else float(v))
        except (KeyError, ValueError):
            continue
        _cand(out, name, rgb_to_hex(*rgb), source, "medium", 4, dark)


def swift_colors(text: str, source: str, out: list) -> None:
    for name, r, g, b, hexv in re.findall(
            r"static\s+(?:let|var)\s+(\w+)\s*=\s*Color\(\s*(?:red:\s*([\d.]+),\s*green:\s*([\d.]+),\s*blue:\s*([\d.]+)|hex:\s*\"#?([0-9A-Fa-f]{6})\")", text):
        val = "#" + hexv if hexv else rgb_to_hex(float(r) * 255, float(g) * 255, float(b) * 255)
        _cand(out, name, val, source, "medium", 3)


# ---------------------------------------------------------------- logo

LOGO_RX = re.compile(r"^(logo|brand|app[-_]?icon|ic_launcher|icon|favicon)([-_.@].*)?$", re.I)
LOGO_EXT = {".svg": 0, ".png": 1, ".webp": 2, ".jpg": 3, ".jpeg": 3, ".ico": 4}


def find_logo(files: list[str]) -> str | None:
    best = None
    for f in files:
        p = PurePosixPath(f)
        m = LOGO_RX.match(p.stem)
        if not m or p.suffix.lower() not in LOGO_EXT:
            continue
        kind = m.group(1).lower().replace("-", "").replace("_", "")
        score = ({"logo": 0, "brand": 1, "appicon": 2, "iclauncher": 2, "icon": 3, "favicon": 4}[kind],
                 LOGO_EXT[p.suffix.lower()], f.count("/"), f)
        best = min(best, score) if best else score
    return best[-1] if best else None


def dominant_color(path: Path) -> str | None:
    """Most common saturated colour in a logo; ignores white/black/grey/transparent pixels."""
    def usable(rgb):
        h = rgb_to_hex(*rgb)
        return saturation(h) > 0.2 and 0.15 < lightness(h) < 0.9
    if path.suffix.lower() == ".svg":
        counts = Counter()
        for v in re.findall(r"(?:fill|stroke|stop-color)\s*[=:]\s*[\"']?(#[0-9A-Fa-f]{3,6})", read_text(path)):
            h = parse_color(v)
            if h and usable(tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))):
                counts[h] += 1
        return counts.most_common(1)[0][0] if counts else None
    try:
        from PIL import Image
    except ImportError:
        return None
    try:
        im = Image.open(path).convert("RGBA")
    except Exception:
        return None
    im.thumbnail((64, 64))
    buckets: dict[tuple, list] = {}
    for r, g, b, a in im.getdata():
        if a > 128 and usable((r, g, b)):
            buckets.setdefault((r // 16, g // 16, b // 16), []).append((r, g, b))
    if not buckets:
        return None
    px = max(buckets.values(), key=len)
    return rgb_to_hex(*(sum(c[i] for c in px) / len(px) for i in range(3)))


# ---------------------------------------------------------------- fonts

def first_family(stack: str) -> str | None:
    for fam in stack.split(","):
        fam = fam.strip().strip("'\"` ").strip()
        if fam and fam.lower() not in GENERIC_FONTS and not fam.startswith(("var(", "$", "--")):
            return fam
    return None


def font_category(name: str) -> str:
    n = name.lower()
    if re.search(r"mono|code|consol|menlo|courier|hack|iosevka", n):
        return "mono"
    if re.search(r"playfair|dm serif|recoleta|fraunces|abril|cormorant|display|bodoni|prata|yeseva", n):
        return "display"
    if re.search(r"serif|georgia|merriweather|lora|times|garamond|crimson|baskerville|libre|spectral|noto serif", n) \
            and "sans" not in n:
        return "serif"
    return "sans"


@lru_cache(maxsize=None)
def _local_font_names() -> frozenset:
    dirs = [Path.home() / "Library/Fonts", Path("/Library/Fonts"), Path("/System/Library/Fonts"),
            Path("/usr/share/fonts"), Path("/usr/local/share/fonts"), Path.home() / ".local/share/fonts",
            Path.home() / ".fonts", Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"]
    names = set()
    for d in dirs:
        if d.is_dir():
            for _, _, files in os.walk(d):
                names.update(re.sub(r"[^a-z0-9]", "", f.lower()) for f in files
                             if f.lower().endswith((".ttf", ".otf", ".ttc", ".woff2")))
    return frozenset(names)


def find_local_font(family: str) -> bool:
    key = re.sub(r"[^a-z0-9]", "", family.lower())
    return any(n.startswith(key) for n in _local_font_names())


def resolve_fonts(cands: list[dict]) -> tuple[dict, dict, list]:
    chosen, sources = {}, {}
    for c in sorted(cands, key=lambda c: CONF_RANK[c["confidence"]]):
        fam = first_family(c["family"])
        if not fam:
            continue
        role = c["role"]
        if role is None:  # unassigned (@font-face, Google link): display/serif -> heading, else body
            role = "heading" if font_category(fam) in ("display", "serif") and "body" in chosen else \
                   "body" if "body" not in chosen else "heading"
        if role not in chosen:
            chosen[role] = fam
            sources[role] = {"source": c["source"], "confidence": c["confidence"]}
    chosen.setdefault("body", None)
    chosen.setdefault("heading", chosen["body"])
    chosen.setdefault("mono", None)
    fonts, subs = {}, []
    for role in ("heading", "body", "mono"):
        fam = chosen[role]
        fallback = "JetBrains Mono" if role == "mono" else "Inter"
        if not fam:
            fonts[role] = fallback
            sources.setdefault(role, {"source": "default", "confidence": "low"})
        elif fam in BUNDLED:
            fonts[role] = fam
        elif find_local_font(fam):
            fonts[role] = fam
            sources[role] = {**sources.get(role, {}), "local": True}
        else:
            used = CATEGORY_FONT["mono" if role == "mono" else font_category(fam)]
            fonts[role] = used
            subs.append({"role": role, "requested": fam, "used": used,
                         "reason": "not bundled and not installed locally"})
    return fonts, sources, subs


# ---------------------------------------------------------------- resolve

def pick(cands: list[dict], role: str) -> dict | None:
    pool = [c for c in cands if c["role"] == role]
    if role in ("primary", "secondary", "accent"):
        # shadcn-style "secondary"/"accent" are pale surface tints, not brand colours
        pool = [c for c in pool if lightness(c["value"]) < 0.85 and saturation(c["value"]) > 0.12]
    if not pool:
        return None
    light = [c for c in pool if not c["dark"]]
    return min(light or pool, key=lambda c: (CONF_RANK[c["confidence"]], c["priority"],
                                             SHADE_PREF.get(c["shade"], 4)))


def build_theme(root: Path, files: list[str], name: str) -> dict | None:
    cands, font_cands, palette = [], [], {}
    for f in files:
        p = PurePosixPath(f)
        low = p.name.lower()
        full = root / f
        if p.suffix in (".css", ".scss", ".sass", ".less", ".pcss"):
            css_colors(read_text(full), f, cands, font_cands)
            google_font_links(read_text(full), f, font_cands)
        elif re.match(r"tailwind\.config\.(js|ts|cjs|mjs)$", low):
            text = read_text(full)
            js_object_colors(text, f, "high", 1, cands)
            tailwind_fonts(text, f, font_cands)
        elif p.suffix in (".js", ".jsx", ".ts", ".tsx", ".mjs"):
            text = read_text(full)
            if re.search(r"(theme|colou?rs|palette|tokens)", p.stem, re.I) or \
                    re.search(r"createTheme|extendTheme|createStyles|ConfigProvider[^>]*theme=|MantineProvider", text):
                js_object_colors(text, f, "medium", 3, cands)
            google_font_links(text, f, font_cands)
        elif p.suffix in (".html", ".htm", ".vue", ".svelte"):
            google_font_links(read_text(full), f, font_cands)
        elif p.suffix == ".dart":
            dart_colors(read_text(full), f, cands, font_cands)
        elif p.suffix == ".xml" and "/res/values" in f:
            android_colors(read_text(full), f, cands, palette)
        elif low == "contents.json" and ".colorset" in f:
            ios_colorset(full, f, cands)
        elif p.suffix == ".swift" and "Color(" in read_text(full):
            swift_colors(read_text(full), f, cands)

    logo = find_logo(files)
    logo_color = dominant_color(root / logo) if logo else None
    colors, sources, notes = {}, {}, []
    for role in ROLES:
        c = pick(cands, role)
        if c:
            colors[role] = c["value"]
            sources[role] = {"source": c["source"], "token": c["name"], "confidence": c["confidence"]}
    if "primary" not in colors:
        # unnamed palette (e.g. AppColors.forest): most saturated mid-tone; else the logo colour
        palette_c = [c for c in cands if c["role"] is None and not c["dark"] and 0.2 < lightness(c["value"]) < 0.7]
        if palette_c:
            c = max(palette_c, key=lambda c: saturation(c["value"]))
            colors["primary"] = c["value"]
            sources["primary"] = {"source": c["source"], "token": c["name"], "confidence": "low"}
        elif logo_color:
            colors["primary"] = logo_color
            sources["primary"] = {"source": logo, "token": "dominant colour", "confidence": "low"}
    if "primary" not in colors:
        return None

    meta = {"detected": True, "sources": sources, "adjustments": [], "dark_mode_mapped": False,
            "substitutions": [], "notes": notes, "logo_dominant": logo_color}
    cover = None
    # Dark-only project: keep brand colours, print on a light page, reuse dark bg for the cover.
    if "bg" in colors and luminance(colors["bg"]) < 0.2:
        meta["dark_mode_mapped"] = True
        dark_bg, dark_text = colors["bg"], colors.get("text", "#f9fafb")
        cover = {"bg": dark_bg, "text": dark_text if contrast(dark_text, dark_bg) >= 4.5 else "#ffffff"}
        colors["bg"] = "#ffffff"
        for role in ("surface", "border", "muted"):
            colors.pop(role, None)
        if luminance(colors.get("text", "#ffffff")) > 0.4:
            darkest = min((c["value"] for c in cands), key=luminance)
            colors["text"] = darkest if contrast(darkest, "#ffffff") >= 7 else DEFAULTS["text"]
            sources["text"] = {"source": "derived", "confidence": "low"}
        notes.append("Dark-only palette mapped to a light print variant; the cover keeps the dark background.")

    # Derive missing roles from what exists.
    p = colors["primary"]
    derived = {
        "secondary": lambda: shift(p, hue_deg=30, light=-0.08),
        "accent": lambda: shift(p, hue_deg=-60),
        "bg": lambda: DEFAULTS["bg"],
        "text": lambda: DEFAULTS["text"],
        "surface": lambda: mix(colors["bg"], p, 0.04),
        "muted": lambda: mix(colors["text"], colors["bg"], 0.45),
        "border": lambda: mix(colors["text"], colors["bg"], 0.85),
        "success": lambda: DEFAULTS["success"], "warning": lambda: DEFAULTS["warning"],
        "danger": lambda: DEFAULTS["danger"],
    }
    for role in ["bg", "text", "secondary", "accent", "surface", "muted", "border", "success", "warning", "danger"]:
        if role not in colors:
            colors[role] = derived[role]()
            sources[role] = {"source": "derived", "confidence": "low"}

    # WCAG: (role, against, target). Text-like roles need 4.5:1; muted captions and accent graphics 3:1.
    checks = [("text", "bg", 4.5), ("text", "surface", 4.5), ("primary", "#ffffff", 4.5),
              ("secondary", "#ffffff", 4.5), ("muted", "bg", 3.0), ("accent", "#ffffff", 3.0),
              ("success", "#ffffff", 4.5), ("warning", "#ffffff", 4.5), ("danger", "#ffffff", 4.5)]
    for role, against, target in checks:
        bg = colors.get(against, against)
        before = contrast(colors[role], bg)
        if before >= target:
            continue
        # Prefer a shade the project already defines (e.g. brand-700) over a computed one.
        shades = [c["value"] for c in cands if c["role"] == role and not c["dark"]
                  and contrast(c["value"], bg) >= target]
        if shades:
            fixed = min(shades, key=lambda v: abs(lightness(v) - lightness(colors[role])))
            moved = abs(lightness(fixed) - lightness(colors[role]))
        else:
            fixed, moved = ensure_contrast(colors[role], bg, target)
        meta["adjustments"].append({"role": role, "from": colors[role], "to": fixed, "against": against,
                                    "ratio_before": round(before, 2), "ratio_after": round(contrast(fixed, bg), 2),
                                    "flagged": moved > 0.30})
        colors[role] = fixed

    fonts, font_sources, subs = resolve_fonts(font_cands)
    meta["sources"].update({f"font_{k}": v for k, v in font_sources.items()})
    meta["substitutions"] = subs
    theme = {"name": f"{name}-detected", "label": f"{name} (detected)", "colors": colors,
             "fonts": fonts, "logo": logo, "meta": meta}
    if cover:
        theme["cover"] = cover
    return theme


def default_theme(name: str) -> dict:
    path = SKILL_DIR / "themes" / f"{name}.json"
    if not path.is_file():
        avail = ", ".join(sorted(p.stem for p in (SKILL_DIR / "themes").glob("*.json")))
        raise SystemExit(json.dumps({"error": f"unknown theme '{name}'", "available": avail}))
    t = load_json(path)
    t["meta"] = {**t.get("meta", {}), "detected": False}
    return t


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__.split("\n\n", 2)[2])
    ap.add_argument("project", type=Path)
    ap.add_argument("--out", type=Path, help="default <project>/docs/.project-docs/theme.json")
    ap.add_argument("--default", default="clean-light", help="theme used when nothing is detected")
    ap.add_argument("--use", metavar="THEME", help="skip detection and write this bundled theme")
    ap.add_argument("--exclude", action="append", default=[], metavar="GLOB")
    args = ap.parse_args(argv)
    if not args.project.is_dir():
        print(json.dumps({"error": f"not a directory: {args.project}"}), file=sys.stderr)
        return 2
    out = args.out or args.project / "docs" / ".project-docs" / "theme.json"

    scanner = Scanner(args.project, args.exclude)
    deps, meta = scanner.manifests()
    has_ui, ui_evidence = scanner.ui(Scanner.frameworks(deps))
    name = meta.get("name") or args.project.resolve().name

    theme = None if args.use else build_theme(args.project, scanner.files, name)
    if theme is None:
        theme = default_theme(args.use or args.default)
        theme["meta"]["notes"] = [f"Using default theme '{theme['name']}'"
                                  + (" (requested)." if args.use else ": no brand colours detected.")]
    theme["meta"]["ui_detected"] = has_ui
    theme["meta"]["ui_evidence"] = ui_evidence
    write_json(out, theme)
    m = theme["meta"]
    print(json.dumps({"out": str(out), "theme": theme["name"], "detected": m["detected"], "ui_detected": has_ui,
                      "colors": theme["colors"], "fonts": theme["fonts"], "logo": theme.get("logo"),
                      "dark_mode_mapped": m.get("dark_mode_mapped", False),
                      "adjustments": m.get("adjustments", []), "substitutions": m.get("substitutions", []),
                      "notes": m.get("notes", [])}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
