"""Catalog, template, theme and SKILL.md validity (Phase 1 exit check)."""
import re
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _common import SKILL_DIR, contrast, load_json  # noqa: E402

CATALOG = yaml.safe_load((SKILL_DIR / "catalog.yaml").read_text())
DOCS = CATALOG["docs"]
IDS = [d["id"] for d in DOCS]
PACKS = [p["id"] for p in CATALOG["packs"]]

REQUIRED = {"id", "title", "audience", "description", "sources_to_scan", "required_inputs",
            "template", "est_pages", "requires_ui", "depends_on", "scan_keys", "pack"}
AUDIENCES = {"planning", "business", "developer", "ops", "user", "governance"}
STAGES = {"planning", "complete", "any"}
INPUT_TYPES = {"text", "number", "money", "choice", "multi", "bool", "list"}
SCAN_KEYS = {"project", "languages", "frameworks", "project_type", "packages", "entry_points",
             "scripts", "openapi", "routes", "database", "infra", "ci", "tests", "env_vars",
             "dependencies", "third_party", "docs", "git", "has_ui"}
ROLES = {"primary", "secondary", "accent", "bg", "surface", "text", "muted", "border",
         "success", "warning", "danger"}
HEX = re.compile(r"^#[0-9a-fA-F]{6}$")


def test_ids_unique():
    assert len(IDS) == len(set(IDS))


@pytest.mark.parametrize("doc", DOCS, ids=IDS)
def test_entry_schema(doc):
    assert REQUIRED <= doc.keys(), REQUIRED - doc.keys()
    assert doc["audience"] in AUDIENCES
    assert doc.get("stage", "complete") in STAGES
    assert isinstance(doc["requires_ui"], bool)
    assert re.fullmatch(r"\d+(-\d+)?", doc["est_pages"])
    assert set(doc["scan_keys"]) <= SCAN_KEYS, set(doc["scan_keys"]) - SCAN_KEYS
    assert doc["pack"] in PACKS
    assert set(doc.get("needs", [])) <= set(doc["scan_keys"]), "needs must be watched scan_keys"
    for d in doc["depends_on"]:
        assert d in IDS, f"{doc['id']} depends on unknown {d}"
        assert d != doc["id"]
    for inp in doc["required_inputs"]:
        assert {"key", "question", "type", "default"} <= inp.keys(), inp
        assert inp["type"] in INPUT_TYPES
        if inp["type"] in ("choice", "multi"):
            assert inp.get("choices"), inp


@pytest.mark.parametrize("doc", DOCS, ids=IDS)
def test_template(doc):
    path = SKILL_DIR / "templates" / doc["template"]
    assert path.is_file(), path
    text = path.read_text()
    front = yaml.safe_load(text.split("---")[1])
    assert front["doc_id"] == doc["id"]
    assert front["title"] == doc["title"]
    assert "## Assumptions and open questions" in text
    assert "<!-- guide:" in text
    if doc["requires_ui"]:
        assert "<!-- variant: cli-api -->" in text, "UI docs need a no-UI variant"


def test_shared_inputs_consistent():
    """An input key asked by several docs must have the same type everywhere (asked once)."""
    seen = {}
    for doc in DOCS:
        for inp in doc["required_inputs"]:
            seen.setdefault(inp["key"], set()).add(inp["type"])
    assert {k: v for k, v in seen.items() if len(v) > 1} == {}


def test_packs():
    assert list(PACKS) == ["planning", "developer", "business", "user", "ops", "handover"]
    assert all({"id", "title", "description"} <= p.keys() for p in CATALOG["packs"])
    assert all(any(d["pack"] == p for d in DOCS) for p in PACKS), "every pack has chapters"


def test_build_plan_is_only_planning_doc():
    assert [d["id"] for d in DOCS if d.get("stage") == "planning"] == ["build-plan"]
    assert [d["id"] for d in DOCS if d["pack"] == "planning"] == ["build-plan"]


THEMES = sorted((SKILL_DIR / "themes").glob("*.json"))


def test_default_themes_present():
    assert {p.stem for p in THEMES} >= {"default", "clean-light", "midnight", "corporate-blue",
                                        "warm-editorial", "mono-minimal"}


@pytest.mark.parametrize("path", THEMES, ids=[p.stem for p in THEMES])
def test_theme(path):
    t = load_json(path)
    assert t["name"] == path.stem
    c = t["colors"]
    assert set(c) == ROLES
    assert all(HEX.match(v) for v in c.values())
    assert set(t["fonts"]) == {"heading", "body", "mono"}
    assert contrast(c["text"], c["bg"]) >= 4.5
    assert contrast(c["text"], c["surface"]) >= 4.5
    assert contrast(c["primary"], "#ffffff") >= 4.5
    assert contrast(c["muted"], c["bg"]) >= 3.0
    for col in (t.get("packs") or {}).values():
        assert contrast("#ffffff", col) >= 4.5
    assert set(t.get("packs") or {}) in (set(), set(PACKS))
    if "cover" in t:
        assert contrast(t["cover"]["text"], t["cover"]["bg"]) >= 4.5


def test_theme_fonts_bundled():
    fonts = SKILL_DIR / "assets" / "fonts"
    bundled = {p.name.split("-")[0] for p in fonts.glob("*.woff2")}
    for path in THEMES:
        for family in load_json(path)["fonts"].values():
            assert family.replace(" ", "") in bundled, family
    for lic in ("Inter", "JetBrainsMono", "SourceSerif4", "Fraunces"):
        assert (fonts / "licenses" / f"{lic}-OFL.txt").is_file()


def test_skill_md():
    text = (SKILL_DIR / "SKILL.md").read_text()
    assert len(text.splitlines()) <= 150
    front = yaml.safe_load(text.split("---")[1])
    assert front["name"] == "project-docs"
    assert len(front["description"]) + len(front.get("when_to_use", "")) <= 1536
    for ref in re.findall(r"`((?:reference|scripts|templates|themes)/[\w./-]+)`", text):
        if ref.startswith("reference/"):
            assert (SKILL_DIR / ref).is_file(), ref


ROOT = SKILL_DIR.parent.parent


def test_plugin_manifests():
    plugin = load_json(ROOT / ".claude-plugin" / "plugin.json")
    market = load_json(ROOT / ".claude-plugin" / "marketplace.json")
    assert plugin["name"] == "project-docs" and re.fullmatch(r"\d+\.\d+\.\d+", plugin["version"])
    assert [p["name"] for p in market["plugins"]] == [plugin["name"]]
    assert market["plugins"][0]["source"] == "./"
    assert (ROOT / "skills" / plugin["name"] / "SKILL.md").is_file()
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert f"## {plugin['version']}" in changelog, "bump CHANGELOG.md with the plugin version"
