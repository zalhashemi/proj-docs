"""build_pdf, verify_pdf, preview_themes: rendering behaviour."""
import json
import os
from pathlib import Path
import shutil

import pytest

import build_pdf
import preview_themes
import verify_pdf
from conftest import FIXTURES

fitz = pytest.importorskip("fitz")

DOC = """---
title: Developer Guide
subtitle: Ledgerline
version: 1.2.0
date: 2026-10-01
author: Platform team
project: Ledgerline
doc_id: dev-guide
confidential: true
---

<!-- guide: this must not appear -->

## Prerequisites

| Tool | Version | Source |
|---|---|---|
| Python | 3.12 | `.python-version` |
| uv | 0.4 ⟨assumption⟩ | not pinned |

> [!ASSUMPTION]
> The team uses uv.

> [!WARNING]
> Never commit `.env`.

## Running

```bash
make dev
```

See [Architecture](architecture.md) and [Runbook](runbook.md).

```mermaid
flowchart LR
  a --> b
```

<div class="gantt">

| Stream | Jan | Feb |
|---|---|---|
| API | ■ | |

</div>

- [x] done
- [ ] todo

Footnote here.[^1]

[^1]: The note.
"""


def _renderer_available():
    # CI sets PROJECT_DOCS_TEST_RENDERER=weasyprint on Linux so both engines get exercised.
    warnings, want = [], os.environ.get("PROJECT_DOCS_TEST_RENDERER", "chromium")
    try:
        r = build_pdf.open_renderer(want, warnings)
    except SystemExit:
        return None
    r.__exit__(None, None, None)
    return r.name


RENDERER = _renderer_available()
needs_renderer = pytest.mark.skipif(RENDERER is None, reason="no PDF renderer (Chromium or WeasyPrint) available")


@pytest.fixture
def docs(tmp_path):
    d = tmp_path / "proj" / "docs"
    (d / ".project-docs").mkdir(parents=True)
    (d / "dev-guide.md").write_text(DOC)
    (d / "architecture.md").write_text("---\ntitle: Architecture\ndoc_id: architecture\n---\n\n## Overview\n\nText.\n")
    shutil.copy(build_pdf.SKILL_DIR / "themes" / "corporate-blue.json", d / ".project-docs" / "theme.json")
    return d


# ---------------------------------------------------------------- pure functions

def test_preprocess_callouts_tags_comments(tmp_path, monkeypatch):
    monkeypatch.setattr(build_pdf.shutil, "which", lambda name: None)  # as if mmdc were absent
    w = []
    out = build_pdf.preprocess(DOC.split("---\n", 2)[2], tmp_path, "dev-guide", w)
    assert "must not appear" not in out
    assert 'class="callout callout-assumption"' in out and "Assumption · unverified" in out
    assert 'class="callout callout-warning"' in out
    assert '<span class="tag tag-assumption">assumption</span>' in out
    assert '<div markdown="1" class="gantt">' in out
    assert any("Mermaid" in x for x in w)


def test_callout_syntax_inside_code_fence_untouched(tmp_path):
    body = "```markdown\n> [!NOTE]\n> literal\n```\n"
    assert "callout" not in build_pdf.preprocess(body, tmp_path, "x", [])


def test_placeholder_warning(tmp_path):
    w = []
    build_pdf.preprocess("Owner: {{owner}}", tmp_path, "x", w)
    assert any("placeholder" in x for x in w)
    w = []
    build_pdf.preprocess("Use `{{name}}` syntax.\n\n```jinja\n{{ x }}\n```\n", tmp_path, "x", w)
    assert not w


def test_postprocess_links_ids_and_gantt(tmp_path):
    (tmp_path / "architecture.md").write_text("x")
    html = build_pdf.md_to_html(build_pdf.preprocess(DOC.split("---\n", 2)[2], tmp_path, "dev-guide", []))
    target = lambda stem, anchor: f"{stem}.pdf" if (tmp_path / f"{stem}.md").is_file() else None
    out = build_pdf.postprocess(html, "dev-guide", tmp_path, target)
    assert 'href="architecture.pdf"' in out
    assert '<span class="missing-link">Runbook</span>' in out
    assert 'id="dev-guide--prerequisites"' in out
    assert 'class="on"' in out
    assert 'class="highlight"' in out
    entries = build_pdf.toc_entries(out, (2, 3))
    assert [e[2] for e in entries] == ["Prerequisites", "Running"]


def test_theme_vars_and_page_css():
    theme = json.loads((build_pdf.SKILL_DIR / "themes" / "midnight.json").read_text())
    v = build_pdf.theme_vars(theme, "letter")
    assert "--cover-bg: #0b1020" in v and "--page-h: 278.4mm" in v and "--warning-tint" in v
    p = build_pdf.page_css(theme, "letter", 'Acme "Pro"', [("doc-x", "Doc X")], True)
    assert "size: Letter" in p and 'Acme \\"Pro\\"' in p and "@page doc-x" in p and "Confidential" in p


def test_pack_colours_and_brand_fallback():
    default = json.loads((build_pdf.SKILL_DIR / "themes" / "default.json").read_text())
    assert build_pdf.pack_color(default, "business") == default["packs"]["business"]
    assert "--pack: " + default["packs"]["ops"] in build_pdf.theme_vars(default, "a4", "ops")
    assert build_pdf.spectrum(default)[1] == default["packs"]["developer"]          # catalog pack order
    brand = json.loads((build_pdf.SKILL_DIR / "themes" / "midnight.json").read_text())   # no packs map
    assert build_pdf.pack_color(brand, "business") == brand["colors"]["primary"]
    assert brand["colors"]["primary"] in build_pdf.spectrum(brand)
    css = build_pdf.page_css(default, "a4", "Acme", [("ch-x-1", "Setup", 1)], False, "user")
    assert "@page ch-x-1 { margin-left: 58mm;" in css and default["packs"]["user"] in css and '"01"' in css


def test_weasyprint_fallback(monkeypatch):
    def broken(self):
        raise build_pdf.RendererUnavailable("WeasyPrint unavailable (no pango)")
    monkeypatch.setattr(build_pdf.WeasyPrintRenderer, "__enter__", broken)
    monkeypatch.setattr(build_pdf.ChromiumRenderer, "__enter__", lambda self: self)
    w = []
    r = build_pdf.open_renderer("weasyprint", w)
    assert r.name == "chromium" and "fell back to chromium" in w[0]


def test_no_renderer_is_a_clear_error(monkeypatch):
    def broken(self):
        raise build_pdf.RendererUnavailable("nope")
    monkeypatch.setattr(build_pdf.WeasyPrintRenderer, "__enter__", broken)
    monkeypatch.setattr(build_pdf.ChromiumRenderer, "__enter__", broken)
    with pytest.raises(SystemExit) as e:
        build_pdf.open_renderer("weasyprint", [])
    assert "no PDF renderer available" in str(e.value)


def test_missing_input_errors(tmp_path):
    with pytest.raises(SystemExit):
        build_pdf.build([tmp_path / "nope.md"], None, None)


# ---------------------------------------------------------------- rendering

@needs_renderer
def test_render_single_doc(docs):
    res = build_pdf.build([docs / "dev-guide.md"], None, None, renderer=RENDERER)
    pdf = docs / "pdf" / "dev-guide.pdf"
    assert res["outputs"] == [str(pdf)] and pdf.is_file()
    d = fitz.open(pdf)
    text = " ".join(p.get_text() for p in d)
    assert d.metadata["title"] == "Developer Guide · Ledgerline"
    assert d.metadata["author"] == "Platform team"
    assert "Contents" in d[1].get_text()
    assert "must not appear" not in text
    assert "Page 2 of" in d[1].get_text() and "Confidential" in d[1].get_text()
    assert d.get_toc()
    # TOC numbers point at the right pages
    toc_text = d[1].get_text()
    running_page = next(i for i, p in enumerate(d) if "make dev" in p.get_text()) + 1
    assert f"Running\n{running_page}" in toc_text or f"Running {running_page}" in toc_text.replace("\n", " ")
    # links to other packs are plain text: their PDF may not exist
    assert not [ln for p in d for ln in p.get_links() if ln["kind"] == fitz.LINK_GOTOR]
    v = verify_pdf.main([str(pdf), "--theme", str(docs / ".project-docs/theme.json"), "--json"])
    assert v == 0
    assert sorted((docs / ".project-docs/preview").glob("dev-guide-p*.png"))


PACK = """---
title: Developer Pack
project: Ledgerline
pack: developer
chapters: [dev-guide, architecture]
---

# Developer Guide {#ch-dev-guide}

## Setup

See [the architecture](#ch-architecture).

# Architecture {#ch-architecture}

## Overview

Text.
"""


@needs_renderer
def test_render_pack_chapters(docs):
    (docs / "developer.md").write_text(PACK)
    res = build_pdf.build([docs / "developer.md"], None, None, renderer=RENDERER)
    assert res["outputs"] == [str(docs / "pdf" / "developer.pdf")]
    d = fitz.open(res["outputs"][0])
    assert [(lvl, t) for lvl, t, _ in d.get_toc()][2:] == [(1, "Developer Guide"), (2, "Setup"),
                                                     (1, "Architecture"), (2, "Overview")]
    setup = next(i for i, p in enumerate(d) if "Setup" in p.get_text() and "Contents" not in p.get_text())
    overview = next(i for i, p in enumerate(d) if "Overview" in p.get_text() and "Contents" not in p.get_text())
    assert overview == setup + 1                       # each chapter opens a page
    assert [ln["page"] for ln in d[setup].get_links()] == [overview]               # in-pack chapter link
    assert verify_pdf.main([res["outputs"][0], "--no-thumbnails"]) == 0


@needs_renderer
def test_combined_pack_and_letter(docs):
    out = docs / "pdf" / "pack.pdf"
    res = build_pdf.build([docs / "dev-guide.md", docs / "architecture.md"], None, out,
                          renderer=RENDERER, combine=True, page_size="letter")
    assert res["outputs"] == [str(out)]
    d = fitz.open(out)
    assert round(d[0].rect.height) == 792  # US Letter
    toc = d[1].get_text()
    assert "Developer Guide" in toc and "Architecture" in toc
    # in a pack, the cross-doc link becomes an internal jump
    assert not [ln for p in d for ln in p.get_links() if ln["kind"] == fitz.LINK_GOTOR]
    assert verify_pdf.main([str(out), "--no-thumbnails"]) == 0


@needs_renderer
def test_idempotent_outputs(docs):
    build_pdf.build([docs / "dev-guide.md"], None, None, renderer=RENDERER)
    first = sorted(p.name for p in (docs / "pdf").iterdir())
    build_pdf.build([docs / "dev-guide.md"], None, None, renderer=RENDERER)
    assert sorted(p.name for p in (docs / "pdf").iterdir()) == first == ["dev-guide.pdf"]


@needs_renderer
def test_detected_logo_on_cover(tmp_path):
    proj = tmp_path / "app"
    shutil.copytree(FIXTURES / "react-tailwind-app", proj)
    (proj / "docs/.project-docs").mkdir(parents=True)
    import detect_theme
    detect_theme.main([str(proj), "--out", str(proj / "docs/.project-docs/theme.json")])
    (proj / "docs/quick-start.md").write_text("---\ntitle: Quick Start\ndoc_id: quick-start\n---\n\n## Go\n\nRun it.\n")
    res = build_pdf.build([proj / "docs/quick-start.md"], None, None, renderer=RENDERER)
    assert not [w for w in res["warnings"] if "logo" in w]
    d = fitz.open(proj / "docs/pdf/quick-start.pdf")
    assert d[0].get_images() or d[0].get_drawings()


# ---------------------------------------------------------------- verify

@needs_renderer
def test_verify_detects_overflow_and_blank(tmp_path):
    html = ("<style>@page{size:A4;margin:0}</style>"
            "<p style='position:absolute;left:-5mm;top:100mm;white-space:nowrap'>overflowing text here</p>"
            "<div style='break-after:page'></div><div style='height:10mm'></div>")
    pdf = tmp_path / "bad.pdf"
    build_pdf.render_html(html, pdf, RENDERER)
    r = verify_pdf.check_pdf(pdf)
    assert any("outside the margins" in e for e in r["errors"])
    assert any("blank page" in e for e in r["errors"])


def test_verify_theme_contrast(tmp_path):
    bad = json.loads((build_pdf.SKILL_DIR / "themes" / "clean-light.json").read_text())
    bad["colors"]["text"] = "#cccccc"
    p = tmp_path / "t.json"
    p.write_text(json.dumps(bad))
    assert any("text on bg" in e for e in verify_pdf.check_theme(p))
    bad = json.loads((build_pdf.SKILL_DIR / "themes" / "default.json").read_text())
    bad["packs"]["user"] = "#f5c400"
    p.write_text(json.dumps(bad))
    assert any("pack 'user'" in e for e in verify_pdf.check_theme(p))


def test_verify_missing_file(tmp_path):
    assert verify_pdf.main([str(tmp_path / "nope.pdf"), "--json"]) == 1


@needs_renderer
def test_preview_themes(tmp_path):
    out = tmp_path / "themes.pdf"
    assert preview_themes.main(["--out", str(out), "--renderer", RENDERER]) == 0
    d = fitz.open(out)
    assert d.page_count == len(list((build_pdf.SKILL_DIR / "themes").glob("*.json")))
    assert len(list(tmp_path.glob("themes-p*.png"))) == d.page_count


@pytest.mark.skipif(not shutil.which("mmdc"), reason="mermaid-cli (mmdc) not installed")
def test_mermaid_rendered_with_theme_and_cached(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path.parent)        # relative docs paths (the common CLI case)
    tmp_path = Path(tmp_path.name)
    theme = json.loads((build_pdf.SKILL_DIR / "themes" / "corporate-blue.json").read_text(encoding="utf-8"))
    body = "```mermaid\nflowchart LR\n  a[Client] --> b[API]\n```\n"
    w = []
    out = build_pdf.preprocess(body, tmp_path, "x", w, theme)
    svgs = list(tmp_path.glob("diagram-*.svg"))
    assert not w and len(svgs) == 1 and svgs[0].resolve().as_uri() in out
    svg = svgs[0].read_text(encoding="utf-8")
    assert "foreignObject" not in svg and "Client" in svg      # plain SVG text: WeasyPrint-safe
    assert theme["colors"]["primary"].lower() in svg.lower()
    mtime = svgs[0].stat().st_mtime
    build_pdf.preprocess(body, tmp_path, "x", [], theme)
    assert svgs[0].stat().st_mtime == mtime                   # cache hit, no re-render


@needs_renderer
def test_toc_pages_by_named_destination(docs):
    """Chromium TOC numbers come from named destinations (heading ids), not from text markers."""
    if RENDERER != "chromium":
        pytest.skip("WeasyPrint computes TOC numbers itself with target-counter()")
    build_pdf.build([docs / "dev-guide.md"], None, None, renderer=RENDERER)
    pages = build_pdf.toc_pages(docs / "pdf" / "dev-guide.pdf", ["dev-guide--prerequisites", "dev-guide--running"])
    assert len(pages) == 2 and all(p >= 3 for p in pages)
