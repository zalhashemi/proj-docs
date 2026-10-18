"""Chromium can print a PDF with @page margin boxes (renderer smoke test)."""
import pytest

fitz = pytest.importorskip("fitz")
sync_api = pytest.importorskip("playwright.sync_api")


def _launch(p):
    # Bundled Playwright Chromium first, then an installed Chrome.
    for kw in ({}, {"channel": "chrome"}):
        try:
            return p.chromium.launch(**kw)
        except Exception:
            continue
    pytest.skip("no Chromium available (run `playwright install chromium` or install Chrome)")


def test_chromium_prints_pdf(tmp_path):
    out = tmp_path / "smoke.pdf"
    html = ("<style>@page{size:A4;margin:20mm;"
            "@bottom-center{content:'Page ' counter(page) ' of ' counter(pages)}}</style>"
            "<h1>Hello</h1>")
    with sync_api.sync_playwright() as p:
        browser = _launch(p)
        page = browser.new_page()
        page.set_content(html)
        page.pdf(path=str(out), prefer_css_page_size=True)
        browser.close()
    text = fitz.open(out)[0].get_text()
    assert "Hello" in text
    assert "Page 1 of 1" in text
