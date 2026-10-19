"""End-to-end: the full skill workflow on each fixture with drafted sample packs.

scan -> theme -> finance charts -> build one PDF per pack + combined -> verify -> record -> diff.
The drafted pack Markdown in sample_docs/ is what Claude would write from the templates.
"""
import json
import shutil
from pathlib import Path

import pytest

import build_pdf
import detect_theme
import finance
import scan_project
import state
import verify_pdf
from test_render import RENDERER, needs_renderer

fitz = pytest.importorskip("fitz")
SAMPLES = Path(__file__).resolve().parent / "sample_docs"
CASES = {  # fixture -> (theme args, expected packs)
    "react-tailwind-app": ([], ["business", "developer", "user"]),
    "fastapi-service": (["--use", "corporate-blue"], ["business", "developer", "ops"]),
    "flutter-app": ([], ["business", "developer", "user"]),
}


@needs_renderer
@pytest.mark.parametrize("fixture", list(CASES))
def test_full_workflow(fixture, fixture_copy, capsys, monkeypatch):
    monkeypatch.setattr(detect_theme, "find_local_font", lambda f: False)
    theme_args, pack_ids = CASES[fixture]
    root = fixture_copy(fixture)
    docs, pd = root / "docs", root / "docs" / ".project-docs"

    assert scan_project.main([str(root)]) == 0
    assert detect_theme.main([str(root), *theme_args]) == 0
    theme = json.loads((pd / "theme.json").read_text())
    if fixture == "fastapi-service":
        assert theme["name"] == "corporate-blue"
    else:
        assert theme["meta"]["detected"] and theme["logo"]

    for md in (SAMPLES / fixture).glob("*.md"):
        shutil.copy(md, docs / md.name)
    shutil.copy(SAMPLES / fixture / "inputs.yaml", pd / "inputs.yaml")
    for kind in ("forecast", "budget"):
        assert finance.main([kind, "--inputs", str(pd / "inputs.yaml"), "--theme", str(pd / "theme.json")]) == 0
    capsys.readouterr()

    res = build_pdf.build(sorted(docs.glob("*.md")), None, None, renderer=RENDERER)
    assert sorted(Path(p).stem for p in res["outputs"]) == pack_ids
    assert not [w for w in res["warnings"] if "placeholder" in w or "logo not found" in w]
    pack = build_pdf.build(sorted(docs.glob("*.md")), None, docs / "pdf" / "docs-pack.pdf",
                           renderer=RENDERER, combine=True)
    pdfs = sorted((docs / "pdf").glob("*.pdf"))
    assert verify_pdf.main([*map(str, pdfs), "--theme", str(pd / "theme.json"), "--json"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["ok"] and len(report["results"]) == len(pack_ids) + 1
    assert list((pd / "preview").glob("business-p*.png"))

    # Forecast charts made it into the business pack; assumptions are visibly tagged.
    biz = fitz.open(docs / "pdf" / "business.pdf")
    assert sum(len(p.get_images()) for p in biz) >= 2
    assert "Assumption" in " ".join(p.get_text() for p in biz)
    assert [t for lvl, t, _ in biz.get_toc() if lvl == 1][1:3] == ["1-Year Forecast", "Budget and Resource Plan"]
    # Combined PDF has every pack, in order. shortcut: chapters are level-1 bookmarks too (flat outline).
    toc_titles = [t for lvl, t, _ in fitz.open(pack["outputs"][0]).get_toc() if lvl == 1]
    assert [t for t in toc_titles if t.endswith(" Pack")] == ["Documentation Pack"] + [
        {"business": "Business Pack", "developer": "Developer Pack", "ops": "Ops Pack", "user": "User Pack"}[i]
        for i in pack_ids]

    # Lifecycle: record, then nothing changed.
    assert state.main(["--docs-dir", str(docs), "set-stage", "complete"]) == 0
    assert state.main(["--docs-dir", str(docs), "record"]) == 0
    capsys.readouterr()
    state.main(["--docs-dir", str(docs), "diff"])
    assert json.loads(capsys.readouterr().out)["changed"] == []


@needs_renderer
def test_rerun_is_idempotent(fixture_copy, capsys):
    root = fixture_copy("fastapi-service")
    docs = root / "docs"
    scan_project.main([str(root)])
    detect_theme.main([str(root), "--use", "clean-light"])
    shutil.copy(SAMPLES / "fastapi-service" / "ops.md", docs / "ops.md")
    for _ in range(2):
        build_pdf.build([docs / "ops.md"], None, None, renderer=RENDERER)
        scan_project.main([str(root)])
    assert sorted(p.name for p in (docs / "pdf").iterdir()) == ["ops.pdf"]
    assert sorted(p.name for p in docs.iterdir()) == [".project-docs", "ops.md", "pdf"]
