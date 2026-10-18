#!/usr/bin/env python3
"""Render project-docs Markdown into branded PDFs (one per document, or a combined pack).

Markdown (tables, fenced code, footnotes, callouts, task lists, front matter) -> HTML -> PDF.
WeasyPrint is the default renderer; --renderer chromium uses Playwright. If the chosen
renderer is unavailable the other one is used and a warning says why.

Usage:
  build_pdf.py docs/dev-guide.md [more.md ...] [--theme docs/.project-docs/theme.json] [--out docs/pdf/]
  build_pdf.py docs/*.md --combine [--out docs/pdf/docs-pack.pdf]
Prints JSON: {"outputs": [...], "renderer": "...", "pages": {...}, "warnings": [...]}
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import hashlib
import io
import html as htmllib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import SKILL_DIR, load_json, mix  # noqa: E402

ASSETS = SKILL_DIR / "assets"
FONT_DIR = ASSETS / "fonts"
FONT_NAMES = {"Inter": "Inter", "JetBrainsMono": "JetBrains Mono", "SourceSerif4": "Source Serif 4",
              "Fraunces": "Fraunces"}
PAGE_SIZES = {"a4": ("A4", 297), "letter": ("Letter", 279.4)}
CALLOUT_TITLES = {"note": "Note", "tip": "Tip", "warning": "Warning", "important": "Important",
                  "caution": "Caution", "assumption": "Assumption · unverified"}


class RendererUnavailable(Exception):
    pass


# ---------------------------------------------------------------- theme -> CSS

def font_faces() -> str:
    rules = []
    for f in sorted(FONT_DIR.glob("*.woff2")):
        parts = f.stem.split("-")
        family = FONT_NAMES.get(parts[0])
        if not family:
            continue
        style = "italic" if "italic" in parts else "normal"
        rules.append(f'@font-face {{ font-family: "{family}"; font-weight: {parts[1]}; '
                     f'font-style: {style}; src: url("{f.as_uri()}") format("woff2"); }}')
    return "\n".join(rules)


def font_stack(name: str, role: str) -> str:
    fallback = '"JetBrains Mono", monospace' if role == "mono" else '"Inter", sans-serif'
    return f'"{name}", {fallback}'


def theme_vars(theme: dict, page_size: str) -> str:
    c = theme["colors"]
    cover = theme.get("cover") or {"bg": c["primary"], "text": "#ffffff"}
    v = {**{k: val for k, val in c.items()},
         "cover-bg": cover["bg"], "cover-text": cover["text"],
         "font-heading": font_stack(theme["fonts"]["heading"], "heading"),
         "font-body": font_stack(theme["fonts"]["body"], "body"),
         "font-mono": font_stack(theme["fonts"]["mono"], "mono"),
         "page-h": f"{PAGE_SIZES[page_size][1] - 1}mm"}
    for role in ("primary", "accent", "success", "warning", "danger"):
        v[f"{role}-tint"] = mix(c[role], "#ffffff", 0.9)
    return ":root {\n" + "\n".join(f"  --{k}: {val};" for k, val in v.items()) + "\n}"


def _css_str(s: str) -> str:
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ") + '"'


def page_css(theme: dict, page_size: str, project: str, named: list[tuple[str, str]], confidential: bool) -> str:
    c = theme["colors"]
    box = f'font-family: {font_stack(theme["fonts"]["body"], "body")}; font-size: 7.5pt; color: {c["muted"]};'
    blank = " ".join(f"@{b} {{ content: none; }}" for b in
                     ("top-left", "top-right", "bottom-left", "bottom-center", "bottom-right"))
    out = [f"""@page {{
  size: {PAGE_SIZES[page_size][0]};
  margin: 22mm 18mm 20mm 18mm;
  @top-left {{ content: ""; {box} }}
  @bottom-left {{ content: {_css_str(project)}; {box} }}
  @bottom-right {{ content: "Page " counter(page) " of " counter(pages); {box} }}
  {f'@bottom-center {{ content: "Confidential"; {box} font-weight: 700; }}' if confidential else ''}
}}""", f"@page cover {{ margin: 0; {blank} }}",
           f'@page toc {{ @top-left {{ content: "Contents"; {box} }} }}']
    for page_name, title in named:
        out.append(f"@page {page_name} {{ @top-left {{ content: {_css_str(title)}; {box} }} }}")
        out.append(f"#{page_name} {{ page: {page_name}; }}")
    return "\n".join(out)


def load_theme(path: Path | None) -> tuple[dict, Path | None]:
    """Returns (theme, project_root) — the root resolves the theme's relative logo path."""
    if path is None or not Path(path).is_file():
        return load_json(SKILL_DIR / "themes" / "clean-light.json"), None
    path = Path(path).resolve()
    root = path.parents[2] if path.parent.name == ".project-docs" else None
    return load_json(path), root


# ---------------------------------------------------------------- markdown

def split_front_matter(text: str) -> tuple[dict, str]:
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        return {}, text
    try:
        import yaml
        data = yaml.safe_load(m.group(1)) or {}
    except Exception:
        data = {}
    return (data if isinstance(data, dict) else {}), text[m.end():]


def render_mermaid(code: str, assets: Path, theme: dict | None) -> str | None:
    """Pre-render a Mermaid block to SVG with mmdc, styled from the theme. Cached by content."""
    mmdc = shutil.which("mmdc")
    if not mmdc:
        return None
    c = (theme or {}).get("colors", {})
    config = {"theme": "base", "htmlLabels": False, "flowchart": {"htmlLabels": False},
              "themeVariables": {"primaryColor": mix(c.get("primary", "#2563eb"), "#ffffff", 0.88),
                                 "primaryBorderColor": c.get("primary", "#2563eb"),
                                 "primaryTextColor": c.get("text", "#111827"),
                                 "lineColor": c.get("muted", "#64748b"),
                                 "secondaryColor": c.get("surface", "#f8fafc"),
                                 "tertiaryColor": c.get("bg", "#ffffff"),
                                 # <img> SVGs can't see the PDF's web fonts: end with system sans fonts
                                 "fontFamily": f'{(theme or {}).get("fonts", {}).get("body", "Inter")}, '
                                               'Helvetica, Arial, sans-serif'}}
    key = hashlib.sha256((code + json.dumps(config, sort_keys=True)).encode()).hexdigest()[:12]
    out = (assets / f"diagram-{key}.svg").resolve()  # file:// URIs need absolute paths
    if out.is_file():
        return out.as_uri()
    assets.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        (t / "d.mmd").write_text(code, encoding="utf-8")
        (t / "config.json").write_text(json.dumps(config), encoding="utf-8")
        (t / "puppeteer.json").write_text('{"args": ["--no-sandbox"]}', encoding="utf-8")  # needed in Linux CI/containers
        try:
            r = subprocess.run([mmdc, "-i", str(t / "d.mmd"), "-o", str(out), "-b", "transparent",
                                "-c", str(t / "config.json"), "-p", str(t / "puppeteer.json")],
                               capture_output=True, timeout=120)
        except (OSError, subprocess.TimeoutExpired):
            return None
    return out.as_uri() if r.returncode == 0 and out.is_file() else None


def preprocess(body: str, assets: Path, doc_id: str, warnings: list, theme: dict | None = None) -> str:
    body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    lines, out, i, fence, n_diag = body.split("\n"), [], 0, None, 0
    while i < len(lines):
        line = lines[i]
        fm = re.match(r"^(\s*)(`{3,}|~{3,})\s*([\w+-]*)", line)
        if fence is None and fm and fm.group(3) == "mermaid":
            code, i = [], i + 1
            while i < len(lines) and not lines[i].strip().startswith(fm.group(2)):
                code.append(lines[i])
                i += 1
            i += 1
            n_diag += 1
            svg = render_mermaid("\n".join(code), assets, theme)
            if svg:
                out += ["", f'<figure class="diagram"><img src="{svg}" alt="Diagram {n_diag}"></figure>', ""]
            else:
                warnings.append(f"{doc_id}: Mermaid diagram {n_diag} shown as code (mermaid-cli 'mmdc' missing or failed)")
                out += ["", '<p class="diagram-fallback note">Diagram not rendered (mermaid-cli missing or failed); source shown below.</p>',
                        "", "```text", *code, "```", ""]
            continue
        if fm:
            fence = None if fence and line.strip().startswith(fence) else (fence or fm.group(2))
            out.append(line)
            i += 1
            continue
        if fence is None and re.fullmatch(r"\s*<div\b(?![^>]*markdown=)[^>]*>\s*", line):
            line = line.replace("<div", '<div markdown="1"', 1)  # let Markdown inside layout divs render
        if fence is None:
            cm = re.match(r"^\s*>\s*\[!(\w+)\]\s*(.*)$", line)
            if cm:
                kind = cm.group(1).lower()
                content = [cm.group(2)] if cm.group(2) else []
                i += 1
                while i < len(lines) and re.match(r"^\s*>", lines[i]):
                    content.append(re.sub(r"^\s*> ?", "", lines[i]))
                    i += 1
                out += ["", f'<div class="callout callout-{kind}" markdown="1">',
                        f'<p class="callout-title">{CALLOUT_TITLES.get(kind, kind.title())}</p>', "",
                        *[_inline_tags(c) for c in content], "", "</div>", ""]
                continue
            line = _inline_tags(line)
        out.append(line)
        i += 1
    prose = re.sub(r"`[^`\n]*`", "", re.sub(r"(`{3,}|~{3,}).*?\1", "", body, flags=re.S))  # code may show {{ }} on purpose
    if "{{" in prose:
        warnings.append(f"{doc_id}: {prose.count('{{')} unfilled {{{{placeholder}}}}(s) left in the Markdown")
    return "\n".join(out)


def _inline_tags(line: str) -> str:
    return re.sub(r"⟨(assumption|untested)⟩", r'<span class="tag tag-\1">\1</span>', line)


def md_to_html(body: str) -> str:
    import markdown
    md = markdown.Markdown(
        extensions=["abbr", "attr_list", "def_list", "footnotes", "md_in_html", "tables", "toc",
                    "sane_lists", "admonition", "pymdownx.superfences", "pymdownx.highlight",
                    "pymdownx.tasklist", "pymdownx.tilde"],
        extension_configs={"pymdownx.highlight": {"css_class": "highlight", "guess_lang": False},
                           "toc": {"permalink": False}})
    return md.convert(body)


def postprocess(html: str, doc_id: str, md_dir: Path, link_target) -> str:
    html = re.sub(r'\bid="([^"]+)"', lambda m: f'id="{doc_id}--{m.group(1)}"', html)
    html = re.sub(r'href="#([^"]+)"', lambda m: f'href="#{doc_id}--{m.group(1)}"', html)

    def md_link(m):
        target = link_target(m.group(1), m.group(2))
        return f'<a href="{target}">{m.group(3)}</a>' if target else f'<span class="missing-link">{m.group(3)}</span>'
    html = re.sub(r'<a href="([\w-]+)\.md(#[^"]*)?"[^>]*>(.*?)</a>', md_link, html)
    html = re.sub(r'src="(?!https?:|file:|data:|/)([^"]+)"',
                  lambda m: f'src="{(md_dir / m.group(1)).resolve().as_uri()}"', html)
    html = re.sub(r'<p>\s*(<img [^>]*alt="([^"]+)"[^>]*>)\s*</p>',
                  r'<figure>\1<figcaption>\2</figcaption></figure>', html)
    html = re.sub(r"<td([^>]*)>\s*■\s*</td>", r'<td\1 class="on"></td>', html)
    # `| | |` key/value tables have an empty header row: drop it and style as key/value.
    html = re.sub(r"<table>\s*<thead>\s*<tr>(?:\s*<th[^>]*>\s*</th>)+\s*</tr>\s*</thead>", '<table class="kv">', html)
    html = html.replace('class="admonition ', 'class="callout callout-').replace("admonition-title", "callout-title")
    return html


def toc_entries(html: str, levels: tuple[int, ...]) -> list[tuple[int, str, str]]:
    out = []
    for m in re.finditer(r'<h([1-4])[^>]*\bid="([^"]+)"[^>]*>(.*?)</h\1>', html, re.S):
        if int(m.group(1)) in levels:
            out.append((int(m.group(1)), m.group(2), htmllib.unescape(re.sub(r"<[^>]+>", "", m.group(3))).strip()))
    return out


def toc_html(entries, mode: str, numbers=None, markers=False) -> str:
    rows = []
    for k, (level, anchor, text) in enumerate(entries):
        if mode == "weasyprint":
            num = f'<a class="toc-num" href="#{anchor}"></a>'
        else:
            num = str(numbers[k]) if numbers else ("000" if markers else "")
        rows.append(f'<tr class="l{level}"><td class="t"><a href="#{anchor}">{htmllib.escape(text)}</a></td>'
                    f'<td class="n">{num}</td></tr>')
    mark = '<span style="font-size:1px;color:transparent">{}</span>'
    return (f'<section class="toc">{mark.format("TOCSTART") if markers else ""}<h2>Contents</h2>'
            f'<table class="toc-table">{"".join(rows)}</table>{mark.format("TOCEND") if markers else ""}</section>')


def cover_html(**ctx) -> str:
    import jinja2
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(ASSETS)), autoescape=True)
    return env.get_template("cover.html.j2").render(**ctx)


def document(title: str, meta: dict, css: str, body: str) -> str:
    metas = "".join(f'<meta name="{k}" content="{htmllib.escape(str(v))}">' for k, v in meta.items() if v)
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{htmllib.escape(title)}</title>'
            f"{metas}<style>{css}</style></head><body>{body}</body></html>")


# ---------------------------------------------------------------- renderers

class WeasyPrintRenderer:
    name = "weasyprint"

    def __enter__(self):
        try:
            # WeasyPrint prints its install help to stdout on failure; keep our JSON clean.
            with contextlib.redirect_stdout(io.StringIO()):
                import weasyprint  # noqa: F401  (needs Pango/Cairo system libraries)
                from weasyprint.text.fonts import FontConfiguration  # noqa: F401
        except Exception as e:  # ImportError, or OSError when Pango is missing
            raise RendererUnavailable(f"WeasyPrint unavailable ({str(e).splitlines()[0][:120]})")
        return self

    def __exit__(self, *exc):
        return False

    def render(self, make_html, out: Path) -> None:
        from weasyprint import HTML
        from weasyprint.text.fonts import FontConfiguration
        HTML(string=make_html(None, False), base_url=str(out.parent)).write_pdf(
            str(out), font_config=FontConfiguration())


class ChromiumRenderer:
    name = "chromium"

    def __enter__(self):
        try:
            from playwright.sync_api import sync_playwright
        except Exception as e:
            raise RendererUnavailable(f"Playwright not installed ({e})")
        self._pw = sync_playwright().start()
        self.browser = launch_chromium(self._pw)
        if self.browser is None:
            self._pw.stop()
            raise RendererUnavailable("no Chromium found; run `playwright install chromium` "
                                      "(downloads ~150 MB, needs network once) or install Google Chrome")
        self._tmp = tempfile.TemporaryDirectory()
        return self

    def __exit__(self, *exc):
        self.browser.close()
        self._pw.stop()
        self._tmp.cleanup()
        return False

    def _print(self, html: str, out: Path) -> None:
        src = Path(self._tmp.name) / "doc.html"
        src.write_text(html, encoding="utf-8")
        page = self.browser.new_page()
        try:
            page.goto(src.as_uri(), wait_until="load")
            page.evaluate("document.fonts.ready")
            page.pdf(path=str(out), prefer_css_page_size=True, print_background=True, outline=True, tagged=True)
        finally:
            page.close()

    def render(self, make_html, out: Path) -> list[str]:
        """Chromium has no target-counter(): pass 1 finds each TOC link's destination page,
        pass 2 prints the numbers (the TOC keeps its size, so pages don't move)."""
        warnings = []
        n_entries = make_html.toc_count
        if not n_entries:
            self._print(make_html(None, False), out)
            return warnings
        self._print(make_html(None, True), out)
        numbers = toc_pages(out, make_html.anchors)
        if len(numbers) != n_entries:
            warnings.append(f"{out.name}: TOC page numbers skipped ({len(numbers)} links for {n_entries} entries)")
            numbers = None
        self._print(make_html(numbers, False), out)
        return warnings


def launch_chromium(pw):
    for kw in ({}, {"channel": "chrome"}, {"channel": "msedge"}):
        try:
            return pw.chromium.launch(**kw)
        except Exception:
            continue
    return None


def toc_pages(pdf: Path, anchors: list[str] | None = None) -> list[int]:
    """1-based page of each TOC entry. Chromium writes a named destination per linked heading id,
    so look anchors up by name; fall back to reading link targets between the TOC markers."""
    import fitz
    doc = fitz.open(pdf)
    names = doc.resolve_names() if hasattr(doc, "resolve_names") else {}
    if anchors and all(a in names for a in anchors):
        doc.close()
        return [names[a]["page"] + 1 for a in anchors]
    pages = [i for i, p in enumerate(doc) if "TOCSTART" in p.get_text() or "TOCEND" in p.get_text()]
    if not pages:
        return []
    links, seen = [], set()
    for pno in range(pages[0], pages[-1] + 1):
        for ln in doc[pno].get_links():
            dest = ln.get("page", -1)
            if dest < 0 and ln.get("nameddest") in names:
                dest = names[ln["nameddest"]].get("page", -1)
            if dest < 0:
                continue
            to = ln.get("to")
            key = (dest, round(to.y, 1) if to is not None else ln.get("nameddest"))
            if key in seen:       # a wrapped title produces two rects with the same destination
                continue
            seen.add(key)
            links.append((pno, ln["from"].y0, ln["from"].x0, dest + 1))
    doc.close()
    return [d for *_, d in sorted(links)]


def open_renderer(preferred: str, warnings: list):
    order = [preferred] + [r for r in ("weasyprint", "chromium") if r != preferred]
    errors = []
    for name in order:
        r = WeasyPrintRenderer() if name == "weasyprint" else ChromiumRenderer()
        try:
            r.__enter__()
        except RendererUnavailable as e:
            errors.append(str(e))
            continue
        if name != preferred:
            warnings.append(f"{errors[0]}; fell back to {name}")
        return r
    raise SystemExit(json.dumps({"error": "no PDF renderer available", "details": errors,
                                 "fix": "pip install playwright && playwright install chromium, "
                                        "or install Pango for WeasyPrint (see README)"}))


def finalize(pdf: Path, title: str, author: str, subject: str, keywords: str) -> int:
    import fitz
    doc = fitz.open(pdf)
    # Renderers turn relative cross-doc links into absolute paths; make them relative
    # "go to file" links so the PDF set still works after it is moved or shared.
    for page in doc:
        for ln in page.get_links():
            target = ln.get("file") or ln.get("uri") or ""
            if target.split("#")[0].endswith(".pdf") and (ln["kind"] == fitz.LINK_LAUNCH or target.startswith("file:")):
                page.delete_link(ln)
                page.insert_link({"kind": fitz.LINK_GOTOR, "from": ln["from"], "page": 0,
                                  "file": Path(target.split("#")[0].replace("file://", "")).name})
    doc.set_metadata({"title": title, "author": author or "", "subject": subject, "keywords": keywords,
                      "creator": "project-docs", "producer": "project-docs"})
    tmp = pdf.with_suffix(".tmp.pdf")
    doc.save(tmp, garbage=3, deflate=True)
    pages = doc.page_count
    doc.close()
    os.replace(tmp, pdf)
    return pages


def render_html(html: str, out: Path, renderer: str = "weasyprint") -> dict:
    """Render a finished HTML string (used by preview_themes.py)."""
    warnings = []
    r = open_renderer(renderer, warnings)
    try:
        make = lambda numbers, markers: html
        make.toc_count, make.anchors = 0, []
        out.parent.mkdir(parents=True, exist_ok=True)
        r.render(make, out)
    finally:
        r.__exit__(None, None, None)
    return {"renderer": r.name, "warnings": warnings}


# ---------------------------------------------------------------- build

def _date(value) -> str:
    s = str(value or "")
    return s if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s) else dt.date.today().isoformat()


def _clean(value) -> str:
    s = str(value or "")
    return "" if "{{" in s else s


def load_doc(path: Path, warnings: list, theme: dict | None = None) -> dict:
    fm, body = split_front_matter(path.read_text(encoding="utf-8"))
    doc_id = re.sub(r"[^\w-]", "-", str(fm.get("doc_id") or path.stem))
    assets = path.parent / ".project-docs" / "assets"
    return {"id": doc_id, "path": path, "fm": fm, "title": _clean(fm.get("title")) or path.stem.replace("-", " ").title(),
            "body": preprocess(body, assets, doc_id, warnings, theme)}


def project_name(docs: list[dict], md_dir: Path) -> str:
    for d in docs:
        if _clean(d["fm"].get("project")):
            return _clean(d["fm"]["project"])
    scan = md_dir / ".project-docs" / "scan.json"
    if scan.is_file():
        try:
            return load_json(scan)["project"]["name"]
        except (KeyError, ValueError):
            pass
    return md_dir.resolve().parent.name


def build(md_paths: list[Path], theme_path: Path | None, out: Path | None, renderer: str = "weasyprint",
          page_size: str = "a4", combine: bool = False, cover: bool = True, toc: bool = True,
          project_root: Path | None = None) -> dict:
    warnings: list[str] = []
    md_paths = [Path(p) for p in md_paths]
    missing = [str(p) for p in md_paths if not p.is_file()]
    if missing:
        raise SystemExit(json.dumps({"error": "input file(s) not found", "files": missing}))
    if len({p.resolve().parent for p in md_paths}) > 1:
        raise SystemExit(json.dumps({"error": "all Markdown inputs must be in the same docs/ folder "
                                              "(theme, assets and output paths are resolved from it)"}))
    md_dir = md_paths[0].parent
    theme, root = load_theme(theme_path or md_dir / ".project-docs" / "theme.json")
    root = project_root or root or md_dir.resolve().parent
    logo = None
    if theme.get("logo"):
        lp = (root / theme["logo"]) if not Path(theme["logo"]).is_absolute() else Path(theme["logo"])
        logo = lp.resolve().as_uri() if lp.is_file() else None
        if not logo:
            warnings.append(f"logo not found: {lp}")
    docs = [load_doc(p, warnings, theme) for p in md_paths]
    project = project_name(docs, md_dir)
    base_css = (ASSETS / "base.css").read_text(encoding="utf-8")
    jobs = []  # (out_path, html parts...)
    if combine:
        ids = {d["id"] for d in docs}
        pack_out = out if out and out.suffix == ".pdf" else (out or md_dir / "pdf") / "docs-pack.pdf"
        jobs.append((pack_out, docs, True))
    else:
        out_dir = out.parent if out and out.suffix == ".pdf" and len(docs) == 1 else (out or md_dir / "pdf")
        for d in docs:
            path = out if out and out.suffix == ".pdf" and len(docs) == 1 else out_dir / f"{d['id']}.pdf"
            jobs.append((path, [d], False))

    r = open_renderer(renderer, warnings)
    outputs, pages = [], {}
    try:
        for pdf_path, group, is_pack in jobs:
            pack_ids = {d["id"] for d in group}

            def link_target(stem, anchor, _pack=is_pack, _ids=pack_ids):
                if _pack:
                    return (f"#{stem}--{anchor[1:]}" if anchor else f"#doc-{stem}") if stem in _ids else None
                return f"{stem}.pdf" if (md_dir / f"{stem}.md").is_file() else None

            bodies, entries, named = [], [], []
            for d in group:
                html = postprocess(md_to_html(d["body"]), d["id"], md_dir, link_target)
                if is_pack:
                    html = f'<h1 class="doc-title" id="doc-{d["id"]}-title">{htmllib.escape(d["title"])}</h1>' + html
                    entries.append((1, f'doc-{d["id"]}-title', d["title"]))
                    entries += toc_entries(html, (2,))
                else:
                    entries += toc_entries(html, (2, 3))
                bodies.append(f'<main class="doc" id="doc-{d["id"]}">{html}</main>')
                named.append((f"doc-{d['id']}", d["title"]))
            fm = group[0]["fm"] if not is_pack else {}
            title = group[0]["title"] if not is_pack else "Documentation Pack"
            confidential = any(bool(d["fm"].get("confidential")) for d in group)
            authors = {_clean(d["fm"].get("author")) for d in group} - {""}
            author = ", ".join(sorted(authors))
            css = "\n".join([font_faces(), theme_vars(theme, page_size), base_css,
                             page_css(theme, page_size, project, named, confidential)])
            cover_part = cover_html(
                logo=logo, project=project, title=title,
                subtitle=_clean(fm.get("subtitle")) if not is_pack else f"{len(group)} documents",
                version=_clean(fm.get("version")), date=_date(fm.get("date")), author=author,
                org=_clean(fm.get("org")), confidential=confidential) if cover else ""
            toc_list = entries if toc else []

            def make_html(numbers, markers, _cover=cover_part, _toc=toc_list, _bodies=bodies, _css=css,
                          _title=title, _author=author):
                toc_part = toc_html(_toc, r.name, numbers, markers) if _toc else ""
                return document(f"{_title} · {project}" if _title != project else _title,
                                {"author": _author, "description": f"{_title} for {project}",
                                 "keywords": "project-docs", "generator": "project-docs"},
                                _css, _cover + toc_part + "".join(_bodies))
            make_html.toc_count = len(toc_list)
            make_html.anchors = [anchor for _, anchor, _ in toc_list]
            pdf_path.parent.mkdir(parents=True, exist_ok=True)
            warnings += r.render(make_html, pdf_path) or []
            pages[str(pdf_path)] = finalize(pdf_path, f"{title} — {project}", author, f"{title} for {project}",
                                            ", ".join(d["id"] for d in group))
            outputs.append(str(pdf_path))
    finally:
        r.__exit__(None, None, None)
    return {"outputs": outputs, "renderer": r.name, "pages": pages, "theme": theme.get("name"), "warnings": warnings}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__.split("\n\n", 1)[1])
    ap.add_argument("markdown", nargs="+", type=Path)
    ap.add_argument("--theme", type=Path, help="theme.json (default <docs>/.project-docs/theme.json, else clean-light)")
    ap.add_argument("--out", type=Path, help="output dir, or a .pdf path for a single doc / --combine")
    ap.add_argument("--renderer", choices=["weasyprint", "chromium"], default="weasyprint")
    ap.add_argument("--page-size", choices=list(PAGE_SIZES), default="a4")
    ap.add_argument("--combine", action="store_true", help="one PDF with a master table of contents")
    ap.add_argument("--no-cover", action="store_true")
    ap.add_argument("--no-toc", action="store_true")
    ap.add_argument("--project-root", type=Path, help="resolves the theme's relative logo path")
    args = ap.parse_args(argv)
    result = build(args.markdown, args.theme, args.out, args.renderer, args.page_size, args.combine,
                   not args.no_cover, not args.no_toc, args.project_root)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
