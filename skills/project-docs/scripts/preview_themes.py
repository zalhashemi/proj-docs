#!/usr/bin/env python3
"""Render a one-page swatch for every theme (bundled + optional extra theme.json files)
into one PDF plus a PNG per page, so themes can be compared side by side.

Usage: preview_themes.py [--extra docs/.project-docs/theme.json] [--out docs/.project-docs/preview/themes.pdf]
"""
from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import SKILL_DIR, contrast, load_json  # noqa: E402
from build_pdf import ASSETS, document, font_faces, page_css, render_html, theme_vars  # noqa: E402
from verify_pdf import thumbnails  # noqa: E402

SAMPLE_CODE = """<pre class="highlight"><code><span class="k">def</span> <span class="nf">invoice_total</span>(items: <span class="nb">list</span>) -&gt; <span class="nb">float</span>:
    <span class="c1"># sum line items, then apply tax</span>
    <span class="k">return</span> <span class="nb">sum</span>(i.price <span class="k">for</span> i <span class="ow">in</span> items) * <span class="mf">1.2</span>  <span class="s2">"EUR"</span></code></pre>"""


def section(theme: dict) -> str:
    c = theme["colors"]
    sid = "t-" + theme["name"]
    cover = theme.get("cover") or {"bg": c["primary"], "text": "#ffffff"}
    chips = "".join(
        f'<td style="background:{c[r]};height:16mm;border:0.6pt solid {c["border"]}"></td>' for r in c)
    labels = "".join(
        f'<td style="font-size:6.2pt;overflow-wrap:normal;word-break:keep-all"><b>{r}</b><br>{c[r]}<br>'
        f'{contrast(c[r], "#ffffff"):.1f}:1 on white</td>' for r in c)
    f = theme["fonts"]
    return f"""<section id="{sid}" class="theme-page" style="break-after: page">
<div style="background:{cover['bg']};color:{cover['text']};padding:7mm 8mm;margin-bottom:6mm">
  <div style="font-family:var(--font-heading);font-size:22pt;font-weight:700">{html.escape(theme.get('label', theme['name']))}</div>
  <div style="font-size:8.5pt;opacity:.9">{html.escape(theme['name'])} · headings {f['heading']} · body {f['body']} · code {f['mono']}</div>
</div>
<table style="table-layout:fixed"><tbody><tr>{chips}</tr><tr>{labels}</tr></tbody></table>
<h2>Heading level two</h2>
<p>Body text in {f['body']}. Text on background is {contrast(c['text'], c['bg']):.1f}:1 and on surface {contrast(c['text'], c['surface']):.1f}:1.
Links look <a href="#">like this</a>, values look like <code>DATABASE_URL</code>, and an unverified value is
tagged <span class="tag tag-assumption">assumption</span>.</p>
<h3>Heading level three</h3>
<table><thead><tr><th>Endpoint</th><th>Method</th><th>Auth</th></tr></thead>
<tbody><tr><td><code>/orders</code></td><td>GET</td><td>API key</td></tr>
<tr><td><code>/orders/{{id}}</code></td><td>DELETE</td><td>API key</td></tr>
<tr><td><code>/health</code></td><td>GET</td><td>none</td></tr></tbody></table>
<div class="callout callout-note"><p class="callout-title">Note</p><p>Callouts use the theme's semantic colours.</p></div>
<div class="callout callout-assumption"><p class="callout-title">Assumption · unverified</p><p>Assumptions get a dashed, hatched frame.</p></div>
{SAMPLE_CODE}
</section>"""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__.split("\n\n", 1)[1])
    ap.add_argument("--extra", type=Path, action="append", default=[], help="additional theme.json (repeatable)")
    ap.add_argument("--out", type=Path, default=Path("docs/.project-docs/preview/themes.pdf"))
    ap.add_argument("--renderer", choices=["weasyprint", "chromium"], default="weasyprint")
    ap.add_argument("--dpi", type=int, default=60)
    args = ap.parse_args(argv)
    themes = [load_json(p) for p in args.extra if p.is_file()] + \
             [load_json(p) for p in sorted((SKILL_DIR / "themes").glob("*.json"))]
    # Each theme's variables are scoped to its own section.
    scoped = "\n".join(theme_vars(t, "a4").replace(":root", f"#t-{t['name']}") for t in themes)
    css = "\n".join([font_faces(), theme_vars(themes[0], "a4"), (ASSETS / "base.css").read_text(encoding="utf-8"),
                     page_css(themes[0], "a4", "project-docs theme previews", [], False), scoped,
                     ".theme-page { color: var(--text); font-family: var(--font-body); }"])
    doc = document("Theme previews", {"generator": "project-docs"}, css, "".join(section(t) for t in themes))
    result = render_html(doc, args.out, args.renderer)
    pngs = thumbnails(args.out, args.out.parent, args.dpi)
    print(json.dumps({"out": str(args.out), "themes": [t["name"] for t in themes], "pngs": pngs, **result}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
