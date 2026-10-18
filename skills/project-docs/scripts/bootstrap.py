#!/usr/bin/env python3
"""Find (or create) the Python environment project-docs needs. Stdlib only.

Prints JSON: {"ready", "python", "missing", "renderers", "mmdc", "venv"}. Use "python" to run
every other script. Exit code 0 when ready, 1 when something must be installed.

Usage:
  bootstrap.py                            check only (no changes)
  bootstrap.py --install                  create the venv and pip-install requirements.txt (network)
  bootstrap.py --install --with-chromium  also download Playwright's Chromium (~150 MB)

Lookup order: $PROJECT_DOCS_PYTHON, <skill>/.venv, $PROJECT_DOCS_VENV or
~/.cache/project-docs/venv (shared by every install of the skill, survives plugin updates),
then the interpreter running this script.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
CORE = ["markdown", "pymdownx", "pygments", "jinja2", "yaml", "PIL", "matplotlib", "fitz"]
PROBE = """
import contextlib, importlib, io, json, sys
out = {"missing": [], "renderers": {}}
for m in %r:
    try: importlib.import_module(m)
    except Exception: out["missing"].append(m)
if sys.version_info < (3, 11):
    try: import tomli
    except Exception: out["missing"].append("tomli")
for name, mod in (("weasyprint", "weasyprint"), ("playwright", "playwright.sync_api")):
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            importlib.import_module(mod)
        out["renderers"][name] = True
    except Exception:
        out["renderers"][name] = False
print(json.dumps(out))
""" % CORE


def venv_dir() -> Path:
    return Path(os.environ.get("PROJECT_DOCS_VENV") or Path.home() / ".cache" / "project-docs" / "venv")


def venv_python(d: Path) -> Path:
    return d / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def probe(python: str) -> dict | None:
    try:
        r = subprocess.run([python, "-c", PROBE], capture_output=True, text=True, timeout=120)
        return json.loads(r.stdout.strip().splitlines()[-1]) if r.returncode == 0 else None
    except (OSError, ValueError, IndexError, subprocess.TimeoutExpired):
        return None


def candidates() -> list[str]:
    out = [os.environ.get("PROJECT_DOCS_PYTHON", ""), str(venv_python(SKILL_DIR / ".venv")),
           str(venv_python(venv_dir())), sys.executable]
    return [c for c in dict.fromkeys(out) if c and Path(c).exists()]


def check() -> dict:
    best = None
    for py in candidates():
        p = probe(py)
        if p is None:
            continue
        ready = not p["missing"] and any(p["renderers"].values())
        result = {"ready": ready, "python": py, **p}
        if ready:
            best = result
            break
        best = best or result
    best = best or {"ready": False, "python": None, "missing": CORE, "renderers": {}}
    best["mmdc"] = bool(shutil.which("mmdc"))
    best["venv"] = str(venv_dir())
    if not best["ready"]:
        best["next"] = f"ask the user, then run: {Path(sys.executable).name} {Path(__file__).as_posix()} --install"
    elif not best["renderers"].get("weasyprint"):
        best["note"] = "WeasyPrint unavailable (needs Pango); PDFs will render with Chromium"
    return best


def install(with_chromium: bool) -> None:
    if sys.version_info < (3, 9):
        raise SystemExit(json.dumps({"error": f"Python 3.9+ required, found {sys.version.split()[0]}"}))
    d = venv_dir()
    if not venv_python(d).exists():
        d.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([sys.executable, "-m", "venv", str(d)], check=True)
    py = str(venv_python(d))
    subprocess.run([py, "-m", "pip", "install", "-q", "--upgrade", "pip"], check=True)
    subprocess.run([py, "-m", "pip", "install", "-q", "-r", str(SKILL_DIR / "requirements.txt")], check=True)
    if with_chromium:
        subprocess.run([py, "-m", "playwright", "install", "chromium"], check=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__.split("\n\n", 1)[1])
    ap.add_argument("--install", action="store_true")
    ap.add_argument("--with-chromium", action="store_true")
    args = ap.parse_args(argv)
    if args.install:
        try:
            install(args.with_chromium)
        except subprocess.CalledProcessError as e:
            print(json.dumps({"error": f"install step failed: {' '.join(map(str, e.cmd))}"}))
            return 2
    result = check()
    print(json.dumps(result, indent=2))
    return 0 if result["ready"] else 1


if __name__ == "__main__":
    sys.exit(main())
