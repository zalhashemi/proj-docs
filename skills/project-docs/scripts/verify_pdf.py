#!/usr/bin/env python3
"""Check rendered PDFs and save PNG thumbnails for visual review.

Checks: page count, blank pages, text outside the page margins, fonts embedded, table of
contents present with resolving links, cross-document links, and theme contrast.
Thumbnails go to docs/.project-docs/preview/<pdf-stem>-pNN.png (pdftoppm if installed,
else PyMuPDF). Exits 1 if any check fails.

Usage: verify_pdf.py docs/pdf/*.pdf [--theme docs/.project-docs/theme.json] [--json] [--dpi 60]
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import contrast, load_json  # noqa: E402

EDGE_MM = 6          # running header/footer sit in the margin; only text this close to the edge fails
MM = 72 / 25.4


def check_pdf(path: Path) -> dict:
    import fitz
    doc = fitz.open(path)
    res = {"file": str(path), "pages": doc.page_count, "errors": [], "warnings": []}
    if doc.page_count == 0:
        res["errors"].append("PDF has no pages")
        return res
    names = doc.resolve_names() if hasattr(doc, "resolve_names") else {}
    fonts, blank, overflow, bad_links, file_links = {}, [], [], [], set()
    for i, page in enumerate(doc):
        r = page.rect
        safe = fitz.Rect(r.x0 + EDGE_MM * MM, r.y0 + EDGE_MM * MM, r.x1 - EDGE_MM * MM, r.y1 - EDGE_MM * MM)
        text = page.get_text().strip()
        if not text and not page.get_images() and not page.get_drawings():
            blank.append(i + 1)
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for span in line["spans"]:
                    b = fitz.Rect(span["bbox"])
                    if span["text"].strip() and span["size"] > 2 and not safe.contains(b):
                        overflow.append(f"p{i + 1}: '{span['text'].strip()[:30]}'")
        for f in page.get_fonts():
            fonts[f[3] or f"{f[2]} font"] = f[1] != "n/a" or f[2] == "Type3"  # Type3 glyphs live in the PDF
        for ln in page.get_links():
            if ln["kind"] == fitz.LINK_GOTO and not (0 <= ln.get("page", -1) < doc.page_count):
                bad_links.append(f"p{i + 1} -> page {ln.get('page')}")
            elif ln["kind"] == fitz.LINK_NAMED and ln.get("nameddest") not in names:
                bad_links.append(f"p{i + 1} -> #{ln.get('nameddest')}")
            elif ln["kind"] in (fitz.LINK_LAUNCH, fitz.LINK_GOTOR) or \
                    (ln["kind"] == fitz.LINK_URI and ln.get("uri", "").endswith(".pdf") and "://" not in ln.get("uri", "")[:8]):
                target = ln.get("file") or ln.get("uri", "")
                file_links.add(target.split("#")[0].replace("file://", ""))
    res["fonts"] = sorted(fonts)
    if blank:
        res["errors"].append(f"blank page(s): {blank}")
    if overflow:
        res["errors"].append(f"{len(overflow)} text span(s) outside the margins, e.g. {overflow[:3]}")
    not_embedded = [f for f, emb in fonts.items() if not emb]
    if not_embedded:
        res["errors"].append(f"fonts not embedded: {not_embedded}")
    early = " ".join(doc[i].get_text() for i in range(min(4, doc.page_count)))
    if doc.page_count > 2 and "Contents" not in early:
        res["errors"].append("no table of contents found in the first pages")
    if doc.page_count > 2 and not doc.get_toc():
        res["warnings"].append("no PDF bookmarks/outline")
    if bad_links:
        res["errors"].append(f"unresolved internal links: {bad_links[:5]}")
    for target in sorted(file_links):
        p = Path(target)
        if not (p if p.is_absolute() else path.parent / p).is_file():
            res["warnings"].append(f"links to {target}, which has not been generated")
    doc.close()
    return res


def check_theme(theme_path: Path) -> list[str]:
    t = load_json(theme_path)
    c = t["colors"]
    errs = []
    for fg, bg, need in (("text", "bg", 4.5), ("text", "surface", 4.5), ("primary", "#ffffff", 4.5),
                         ("muted", "bg", 3.0)):
        ratio = contrast(c[fg], c.get(bg, bg))
        if ratio < need:
            errs.append(f"theme contrast {fg} on {bg} is {ratio:.2f}:1 (needs {need}:1)")
    for pack, col in (t.get("packs") or {}).items():   # white band and cover text sit on each pack colour
        if contrast("#ffffff", col) < 4.5:
            errs.append(f"theme contrast white on pack '{pack}' is {contrast('#ffffff', col):.2f}:1 (needs 4.5:1)")
    cover = t.get("cover") or {"bg": c["primary"], "text": "#ffffff"}
    if contrast(cover["text"], cover["bg"]) < 4.5:
        errs.append(f"cover text contrast {contrast(cover['text'], cover['bg']):.2f}:1 (needs 4.5:1)")
    return errs


def thumbnails(pdf: Path, out_dir: Path, dpi: int) -> list[str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob(f"{pdf.stem}-p*.png"):
        old.unlink()  # idempotent: no stale pages from a longer previous render
    if shutil.which("pdftoppm"):
        subprocess.run(["pdftoppm", "-png", "-r", str(dpi), str(pdf), str(out_dir / f"{pdf.stem}-p")],
                       check=True, capture_output=True)
        for f in out_dir.glob(f"{pdf.stem}-p-*.png"):  # pdftoppm names: stem-p-01.png
            f.rename(out_dir / f"{pdf.stem}-p{int(f.stem.rsplit('-', 1)[1]):02d}.png")
    else:
        import fitz
        with fitz.open(pdf) as doc:
            for i, page in enumerate(doc):
                page.get_pixmap(dpi=dpi).save(out_dir / f"{pdf.stem}-p{i + 1:02d}.png")
    return sorted(str(p) for p in out_dir.glob(f"{pdf.stem}-p*.png"))


def default_preview_dir(pdf: Path) -> Path:
    # docs/pdf/x.pdf -> docs/.project-docs/preview
    if pdf.parent.name == "pdf":
        return pdf.parent.parent / ".project-docs" / "preview"
    return pdf.parent / "preview"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__.split("\n\n", 1)[1])
    ap.add_argument("pdfs", nargs="+", type=Path)
    ap.add_argument("--theme", type=Path)
    ap.add_argument("--preview-dir", type=Path)
    ap.add_argument("--dpi", type=int, default=60)
    ap.add_argument("--no-thumbnails", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to cp1252
    results = []
    for pdf in args.pdfs:
        if not pdf.is_file():
            results.append({"file": str(pdf), "errors": ["file not found"], "warnings": []})
            continue
        try:
            r = check_pdf(pdf)
        except Exception as e:  # corrupt PDF
            r = {"file": str(pdf), "errors": [f"cannot open: {e}"], "warnings": []}
        if not args.no_thumbnails and not r["errors"][:1] == ["file not found"] and "pages" in r:
            r["thumbnails"] = thumbnails(pdf, args.preview_dir or default_preview_dir(pdf), args.dpi)
        results.append(r)
    theme_errors = check_theme(args.theme) if args.theme and args.theme.is_file() else []
    ok = not theme_errors and all(not r["errors"] for r in results)
    if args.json:
        print(json.dumps({"ok": ok, "theme_errors": theme_errors, "results": results}, indent=2))
    else:
        for r in results:
            status = "PASS" if not r["errors"] else "FAIL"
            print(f"{status}  {r['file']}  ({r.get('pages', '?')} pages)")
            for e in r["errors"]:
                print(f"      error: {e}")
            for w in r["warnings"]:
                print(f"      warn:  {w}")
            if r.get("thumbnails"):
                print(f"      thumbnails: {Path(r['thumbnails'][0]).parent}/{Path(r['file']).stem}-pNN.png")
        for e in theme_errors:
            print(f"FAIL  theme: {e}")
        print("OK" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
