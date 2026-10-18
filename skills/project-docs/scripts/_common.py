"""Shared helpers for project-docs scripts (stdlib only)."""
from __future__ import annotations

import colorsys
import fnmatch
import json
import math
import os
import re
import subprocess
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent

SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "env", "__pycache__", "dist", "build", "out",
             ".next", ".nuxt", ".svelte-kit", "target", "vendor", "coverage", ".pytest_cache",
             ".mypy_cache", ".ruff_cache", ".tox", ".gradle", ".idea", ".dart_tool", "Pods",
             ".turbo", ".cache", ".parcel-cache", ".expo", "bower_components", ".terraform"}
MAX_FILES = 20000
MAX_READ_BYTES = 256 * 1024


# ---------------------------------------------------------------- files

def _gitignore_patterns(root: Path) -> list[str]:
    try:
        lines = (root / ".gitignore").read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return []
    return [l.strip().rstrip("/") for l in lines if l.strip() and not l.startswith(("#", "!"))]


def _ignored(rel: str, patterns: list[str]) -> bool:
    parts = rel.split("/")
    for p in patterns:
        p = p.lstrip("/")
        if "/" in p:
            if fnmatch.fnmatch(rel, p) or rel.startswith(p + "/"):
                return True
        elif any(fnmatch.fnmatch(part, p) for part in parts):
            return True
    return False


def list_files(root: Path, excludes: list[str] | None = None) -> list[str]:
    """Relative POSIX paths of project files, honouring .gitignore and SKIP_DIRS."""
    root = Path(root)
    excludes = list(excludes or []) + ["docs/.project-docs/*"]
    files = None
    if (root / ".git").exists():
        out = git(root, "ls-files", "-co", "--exclude-standard")
        if out is not None:
            files = [f for f in out.splitlines() if f]
    if files is None:
        # shortcut: top-level .gitignore only, no negation rules; fine for non-git dirs.
        patterns = _gitignore_patterns(root)
        files = []
        for dirpath, dirnames, filenames in os.walk(root):
            rel_dir = Path(dirpath).relative_to(root).as_posix()
            rel_dir = "" if rel_dir == "." else rel_dir + "/"
            dirnames[:] = sorted(d for d in dirnames
                                 if d not in SKIP_DIRS and not _ignored(rel_dir + d, patterns))
            for name in sorted(filenames):
                rel = rel_dir + name
                if not _ignored(rel, patterns):
                    files.append(rel)
            if len(files) > MAX_FILES:
                break
    keep = []
    for f in files:
        if any(part in SKIP_DIRS for part in f.split("/")[:-1]):
            continue
        if any(fnmatch.fnmatch(f, e) or f.startswith(e.rstrip("/*") + "/") for e in excludes):
            continue
        keep.append(f)
    return sorted(keep)[:MAX_FILES]


def read_text(path: Path, cap: int = MAX_READ_BYTES) -> str:
    """Read up to `cap` bytes as text; '' for binary or unreadable files."""
    try:
        with open(path, "rb") as fh:
            data = fh.read(cap)
    except OSError:
        return ""
    if b"\0" in data[:1024]:
        return ""
    return data.decode("utf-8", errors="ignore")


def git(root: Path, *args: str) -> str | None:
    try:
        r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True,
                           timeout=20)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return r.stdout if r.returncode == 0 else None


def load_json(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path: Path, data) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- colour

def hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def rgb_to_hex(r: float, g: float, b: float) -> str:
    return "#" + "".join(f"{max(0, min(255, round(c))):02x}" for c in (r, g, b))


def luminance(h: str) -> float:
    """WCAG 2.x relative luminance."""
    def chan(c: int) -> float:
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = hex_to_rgb(h)
    return 0.2126 * chan(r) + 0.7152 * chan(g) + 0.0722 * chan(b)


def contrast(fg: str, bg: str) -> float:
    a, b = sorted((luminance(fg), luminance(bg)), reverse=True)
    return (a + 0.05) / (b + 0.05)


def _hls(h: str) -> tuple[float, float, float]:
    r, g, b = (c / 255 for c in hex_to_rgb(h))
    return colorsys.rgb_to_hls(r, g, b)


def _from_hls(h: float, l: float, s: float) -> str:
    r, g, b = colorsys.hls_to_rgb(h % 1.0, max(0.0, min(1.0, l)), max(0.0, min(1.0, s)))
    return rgb_to_hex(r * 255, g * 255, b * 255)


def lightness(h: str) -> float:
    return _hls(h)[1]


def saturation(h: str) -> float:
    return _hls(h)[2]


def shift(h: str, *, hue_deg: float = 0, light: float = 0) -> str:
    hh, l, s = _hls(h)
    return _from_hls(hh + hue_deg / 360, l + light, s)


def mix(a: str, b: str, t: float) -> str:
    """t=0 -> a, t=1 -> b."""
    ra, rb = hex_to_rgb(a), hex_to_rgb(b)
    return rgb_to_hex(*(x + (y - x) * t for x, y in zip(ra, rb)))


def ensure_contrast(fg: str, bg: str, target: float = 4.5) -> tuple[str, float]:
    """Darken (or lighten, on dark bg) fg in small lightness steps until it meets target.
    Returns (colour, total lightness shift)."""
    step = -0.02 if luminance(bg) > 0.4 else 0.02
    hh, l0, s = _hls(fg)
    out, l = fg, l0
    while contrast(out, bg) < target and 0.0 < l < 1.0:
        l += step
        out = _from_hls(hh, l, s)
    return out, abs(l - l0)


def _oklch_to_hex(L: float, C: float, H: float) -> str:
    a, b = C * math.cos(math.radians(H)), C * math.sin(math.radians(H))
    l_ = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m_ = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s_ = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    lin = (4.0767416621 * l_ - 3.3077115913 * m_ + 0.2309699292 * s_,
           -1.2684380046 * l_ + 2.6097574011 * m_ - 0.3413193965 * s_,
           -0.0041960863 * l_ - 0.7034186147 * m_ + 1.7076147010 * s_)
    gam = [12.92 * c if c <= 0.0031308 else 1.055 * max(c, 0) ** (1 / 2.4) - 0.055 for c in lin]
    return rgb_to_hex(*(c * 255 for c in gam))


_NUM = r"(-?[\d.]+)(%?)"


def parse_color(value: str) -> str | None:
    """Parse CSS/Flutter/shadcn colour syntaxes into '#rrggbb'. None if not a colour."""
    v = value.strip().strip("'\"").strip().lower()
    if m := re.fullmatch(r"#([0-9a-f]{3}|[0-9a-f]{6}|[0-9a-f]{8})", v):
        h = m.group(1)
        return "#" + ("".join(c * 2 for c in h) if len(h) == 3 else h[:6])
    if m := re.fullmatch(r"0x([0-9a-f]{8})", v):           # Flutter 0xAARRGGBB
        return "#" + m.group(1)[2:]
    nums = [(float(n), pct) for n, pct in re.findall(_NUM, v.split("/")[0])]
    if v.startswith("rgb") and len(nums) >= 3:
        return rgb_to_hex(*(n * 2.55 if p else n for n, p in nums[:3]))
    if v.startswith("hsl") or (re.fullmatch(r"[\d.]+(deg)?\s+[\d.]+%\s+[\d.]+%", v)):
        if len(nums) >= 3:                                  # also shadcn bare triplets
            h, s, l = nums[0][0], nums[1][0] / 100, nums[2][0] / 100
            return _from_hls(h / 360, l, s)
    if v.startswith("oklch") and len(nums) >= 3:
        L = nums[0][0] / 100 if nums[0][1] else nums[0][0]
        C = nums[1][0] / 100 * 0.4 if nums[1][1] else nums[1][0]
        return _oklch_to_hex(L, C, nums[2][0])
    return {"white": "#ffffff", "black": "#000000"}.get(v)
