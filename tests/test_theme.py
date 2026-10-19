"""detect_theme.py: fixtures, framework variants, fallbacks, contrast and dark mapping."""
import json

import pytest

import detect_theme
from _common import contrast, ensure_contrast, parse_color
from conftest import FIXTURES


@pytest.fixture(autouse=True)
def no_local_fonts(monkeypatch):
    # Results must not depend on which fonts this machine has installed.
    monkeypatch.setattr(detect_theme, "find_local_font", lambda family: False)


def run(project, tmp_path, *extra):
    out = tmp_path / "theme.json"
    assert detect_theme.main([str(project), "--out", str(out), *extra]) == 0
    return json.loads(out.read_text())


def assert_print_safe(t):
    c = t["colors"]
    assert contrast(c["text"], c["bg"]) >= 4.5
    assert contrast(c["text"], c["surface"]) >= 4.5
    assert contrast(c["primary"], "#ffffff") >= 4.5
    assert contrast(c["muted"], c["bg"]) >= 3.0
    assert set(c) == set(detect_theme.ROLES)


def test_react_fixture(tmp_path):
    t = run(FIXTURES / "react-tailwind-app", tmp_path)
    m = t["meta"]
    assert m["detected"] and m["ui_detected"]
    assert m["sources"]["primary"]["source"] == "tailwind.config.js"
    assert m["sources"]["primary"]["confidence"] == "high"
    # brand #14b8a6 fails on white -> project's own brand-700 is used instead of a computed shade
    adj = next(a for a in m["adjustments"] if a["role"] == "primary")
    assert adj["from"] == "#14b8a6" and adj["to"] == "#0f766e"
    assert t["colors"]["text"] == "#1e293b"          # 'ink' token
    assert t["colors"]["bg"] == "#ffffff" and t["colors"]["border"] == "#e2e8f0"
    assert t["fonts"] == {"heading": "Fraunces", "body": "Inter", "mono": "JetBrains Mono"}
    assert {s["requested"] for s in m["substitutions"]} == {"Poppins", "Playfair Display"}
    assert t["logo"] == "public/logo.svg"
    assert m["logo_dominant"] == "#14b8a6"
    assert_print_safe(t)


def test_fastapi_falls_back_to_default(tmp_path):
    t = run(FIXTURES / "fastapi-service", tmp_path)
    assert t["name"] == "default" and t["meta"]["detected"] is False
    assert t["meta"]["ui_detected"] is False
    t = run(FIXTURES / "fastapi-service", tmp_path, "--default", "corporate-blue")
    assert t["name"] == "corporate-blue"


def test_flutter_fixture(tmp_path):
    t = run(FIXTURES / "flutter-app", tmp_path)
    assert t["colors"]["primary"] == "#2e7d32"
    assert t["colors"]["secondary"] == "#00695c"
    assert t["colors"]["surface"] == "#f4f7f2"
    assert t["meta"]["sources"]["primary"]["source"] == "lib/theme/app_theme.dart"
    assert t["logo"] == "assets/images/logo.png"
    assert t["meta"]["logo_dominant"] is not None
    assert t["meta"]["substitutions"][0]["requested"] == "Nunito"
    assert_print_safe(t)


def test_use_default_theme(tmp_path):
    t = run(FIXTURES / "react-tailwind-app", tmp_path, "--use", "midnight")
    assert t["name"] == "midnight" and t["cover"]["bg"] == "#0b1020"


def test_unknown_theme_errors(tmp_path):
    with pytest.raises(SystemExit):
        detect_theme.main([str(tmp_path), "--use", "nope", "--out", str(tmp_path / "t.json")])


def test_tailwind_v4_and_shadcn(tmp_path):
    (tmp_path / "app.css").write_text("""
@import "tailwindcss";
@theme {
  --color-primary: oklch(0.55 0.2 260);
  --font-sans: "Geist", sans-serif;
  --font-mono: "Fira Code", monospace;
}
:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  --secondary: 210 40% 96.1%;
  --muted-foreground: 215.4 16.3% 46.9%;
  --border: 214.3 31.8% 91.4%;
  --destructive: 0 84.2% 60.2%;
}
.dark { --background: 222.2 84% 4.9%; --foreground: 210 40% 98%; }
""")
    t = run(tmp_path, tmp_path)
    c, src = t["colors"], t["meta"]["sources"]
    assert src["primary"]["confidence"] == "high"
    assert c["bg"] == "#ffffff"                       # light value wins over .dark
    assert c["text"] == parse_color("222.2 84% 4.9%")
    assert src["secondary"]["source"] == "derived"    # pale shadcn 'secondary' rejected
    assert t["fonts"]["mono"] == "JetBrains Mono"
    assert {s["requested"] for s in t["meta"]["substitutions"]} == {"Geist", "Fira Code"}
    assert_print_safe(t)


def test_mui_theme_object(tmp_path):
    (tmp_path / "theme.ts").write_text("""
import { createTheme } from '@mui/material/styles';
export const theme = createTheme({
  palette: {
    primary: { main: '#6a1b9a', light: '#9c4dcc' },
    secondary: { main: '#00838f' },
    background: { default: '#fafafa', paper: '#ffffff' },
    text: { primary: '#212121', secondary: '#616161' },
  },
});
""")
    t = run(tmp_path, tmp_path)
    c = t["colors"]
    assert (c["primary"], c["secondary"], c["bg"], c["surface"], c["text"], c["muted"]) == \
        ("#6a1b9a", "#00838f", "#fafafa", "#ffffff", "#212121", "#616161")


def test_android_and_ios(tmp_path):
    res = tmp_path / "android/app/src/main/res/values"
    res.mkdir(parents=True)
    (res / "colors.xml").write_text('<resources><color name="brand_red">#FFC62828</color></resources>')
    (res / "themes.xml").write_text('<resources><style name="AppTheme">'
                                    '<item name="colorPrimary">@color/brand_red</item></style></resources>')
    cs = tmp_path / "ios/App/Assets.xcassets/AccentColor.colorset"
    cs.mkdir(parents=True)
    (cs / "Contents.json").write_text(json.dumps({"colors": [{"idiom": "universal", "color": {
        "color-space": "srgb", "components": {"red": "0.000", "green": "0.400", "blue": "0.500", "alpha": "1.000"}}}]}))
    t = run(tmp_path, tmp_path)
    assert t["colors"]["primary"] == "#c62828"
    assert t["meta"]["sources"]["accent"]["source"].endswith("Contents.json")


def test_dark_only_project_mapped(tmp_path):
    (tmp_path / "styles.css").write_text(
        ":root { --background: #0f172a; --foreground: #e2e8f0; --primary: #38bdf8; --surface: #1e293b; }")
    t = run(tmp_path, tmp_path)
    m = t["meta"]
    assert m["dark_mode_mapped"] is True
    assert t["colors"]["bg"] == "#ffffff"
    assert t["cover"] == {"bg": "#0f172a", "text": "#e2e8f0"}
    assert any(a["role"] == "primary" for a in m["adjustments"])   # light sky blue darkened
    assert_print_safe(t)


def test_logo_only_project(tmp_path):
    pytest.importorskip("PIL")
    from PIL import Image
    (tmp_path / "assets").mkdir()
    Image.new("RGB", (32, 32), (200, 30, 90)).save(tmp_path / "assets/logo.png")
    t = run(tmp_path, tmp_path)
    assert t["meta"]["sources"]["primary"]["confidence"] == "low"
    assert t["logo"] == "assets/logo.png"
    assert_print_safe(t)


def test_role_mapping():
    r = detect_theme.role_of
    assert r("theme-extend-colors-brand-DEFAULT")[:2] == ("primary", "default")
    assert r("text-primary")[0] == "text"
    assert r("text-secondary")[0] == "muted"
    assert r("primary-foreground")[0] is None
    assert r("colorPrimary")[0] == "primary"
    assert r("palette-background-paper")[0] == "surface"
    assert r("dark-primary")[2] is True


def test_parse_color_variants():
    assert parse_color("#abc") == "#aabbcc"
    assert parse_color("#11223344") == "#112233"
    assert parse_color("rgb(255, 0, 0)") == "#ff0000"
    assert parse_color("rgb(0 128 0 / 50%)") == "#008000"
    assert parse_color("hsl(0, 100%, 50%)") == "#ff0000"
    assert parse_color("0 0% 100%") == "#ffffff"
    assert parse_color("0xFF2E7D32") == "#2e7d32"
    assert parse_color("oklch(1 0 0)") == "#ffffff"
    assert parse_color("oklch(62.8% 0.2577 29.23)") in ("#ff0000", "#fe0000", "#ff0001")
    assert parse_color("var(--x)") is None


def test_ensure_contrast():
    fixed, moved = ensure_contrast("#facc15", "#ffffff", 4.5)
    assert contrast(fixed, "#ffffff") >= 4.5 and moved > 0
    fixed, _ = ensure_contrast("#1e293b", "#0f172a", 4.5)   # dark bg -> lightens
    assert contrast(fixed, "#0f172a") >= 4.5


def test_large_shift_flagged(tmp_path):
    (tmp_path / "s.css").write_text(":root { --primary: #fde047; }")   # pale yellow
    adj = run(tmp_path, tmp_path)["meta"]["adjustments"]
    assert next(a for a in adj if a["role"] == "primary")["flagged"] is True
