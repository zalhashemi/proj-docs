"""scan_project.py on the fixtures plus degradation cases."""
import json

import pytest

import scan_project
from conftest import FIXTURES


@pytest.fixture(scope="module")
def scans():
    return {name: scan_project.scan(FIXTURES / name)
            for name in ("react-tailwind-app", "fastapi-service", "flutter-app")}


def test_all_scan_keys_present(scans):
    keys = {"project", "languages", "frameworks", "project_type", "packages", "entry_points", "scripts",
            "openapi", "routes", "database", "infra", "ci", "tests", "env_vars", "dependencies",
            "third_party", "docs", "git", "has_ui"}
    for data in scans.values():
        assert keys <= data.keys()
        json.dumps(data)  # serialisable


def test_react(scans):
    d = scans["react-tailwind-app"]
    assert d["project"]["name"] == "brightcart" and d["project"]["version"] == "1.4.0"
    assert {"React", "Tailwind CSS", "Vite"} <= set(d["frameworks"])
    assert d["project_type"]["primary"] == "web app"
    assert d["has_ui"] is True
    assert {s["name"] for s in d["scripts"]} == {"dev", "build", "preview", "lint", "test"}
    assert {e["name"] for e in d["env_vars"]} == {"VITE_API_URL", "VITE_SENTRY_DSN", "VITE_STRIPE_PUBLISHABLE_KEY"}
    assert d["ci"][0]["system"] == "GitHub Actions" and d["ci"][0]["secrets"] == ["VERCEL_TOKEN"]
    assert "Vitest" in d["tests"]["frameworks"] and d["tests"]["cases_approx"] == 2
    assert {t["service"] for t in d["third_party"]} >= {"Sentry", "Stripe"}
    assert "vercel.json" in d["infra"]["platform_configs"]
    assert d["stage_hint"] == "active"


def test_fastapi(scans):
    d = scans["fastapi-service"]
    assert d["has_ui"] is False
    assert d["project_type"]["all"][0] == "API/service" and "CLI" in d["project_type"]["all"]
    routes = {(r["method"], r["path"]) for r in d["routes"]}
    assert routes == {("GET", "/health"), ("GET", "/orders"), ("POST", "/orders"),
                      ("GET", "/orders/{order_id}"), ("DELETE", "/orders/{order_id}")}
    assert {m["name"] for m in d["database"]["models"]} == {"Customer", "Order"}
    assert d["database"]["engines"] == ["PostgreSQL"]
    assert d["database"]["migrations"] == [{"dir": "alembic/versions", "count": 2}]
    assert {s["name"] for s in d["scripts"]} >= {"dev", "test", "lint", "migrate", "ledgerline"}
    env = {e["name"]: e for e in d["env_vars"]}
    assert set(env) == {"DATABASE_URL", "API_KEY", "SENTRY_DSN", "AWS_S3_BUCKET"}
    assert "app/auth.py" in env["API_KEY"]["sources"]
    assert d["infra"]["compose"][0]["services"] == ["api", "db"]
    assert d["ci"][0]["system"] == "GitLab CI"
    assert d["tests"]["coverage_config"] == ["pyproject.toml"]
    assert d["docs"]["license_type"] == "MIT"


def test_flutter(scans):
    d = scans["flutter-app"]
    assert d["frameworks"] == ["Flutter"]
    assert d["project_type"]["primary"] == "mobile app"
    assert d["has_ui"] is True
    assert "Firestore" in d["database"]["engines"]
    assert d["tests"]["frameworks"] == ["flutter_test"]


def test_never_leaks_env_values(scans):
    blob = json.dumps(scans)
    for secret in ("pk_test_FIXTURE_DO_NOT_LEAK", "change-me", "ledger:ledger"):
        assert secret not in blob


def test_empty_dir(tmp_path):
    d = scan_project.scan(tmp_path)
    assert d["project_type"]["primary"] == "unknown"
    assert d["git"] == {"is_repo": False}
    assert d["stage_hint"] == "planning"
    assert d["has_ui"] is False


def test_unknown_stack_and_binary(tmp_path):
    (tmp_path / "main.zig").write_text("const std = @import(\"std\");\n")
    (tmp_path / "blob.bin").write_bytes(b"\0\1\2" * 100)
    (tmp_path / "broken.json").write_text("{not json")
    (tmp_path / "package.json").write_text("{ broken")
    d = scan_project.scan(tmp_path)
    assert d["project"]["name"] == tmp_path.name
    assert d["frameworks"] == []


def test_skips_vendored_and_gitignored(tmp_path):
    (tmp_path / "node_modules/x").mkdir(parents=True)
    (tmp_path / "node_modules/x/index.js").write_text("process.env.SHOULD_NOT_APPEAR")
    (tmp_path / "generated").mkdir()
    (tmp_path / "generated/a.py").write_text("import os\nos.getenv('IGNORED_VAR')")
    (tmp_path / ".gitignore").write_text("generated/\n")
    (tmp_path / "app.py").write_text("import os\nos.getenv('KEPT_VAR')")
    names = {e["name"] for e in scan_project.scan(tmp_path)["env_vars"]}
    assert names == {"KEPT_VAR"}


def test_git_repo(fixture_copy, git_repo):
    d = scan_project.scan(git_repo(fixture_copy("fastapi-service")))
    g = d["git"]
    assert g["is_repo"] and g["commits"] == 1 and g["contributors"] == 1
    assert g["tags"][0]["name"] == "v0.1.0"
    assert g["remote_url"] == "https://example.com/acme/app.git"  # credentials stripped


def test_exclude(tmp_path):
    (tmp_path / "keep.py").write_text("import os\nos.getenv('AA')")
    (tmp_path / "fx").mkdir()
    (tmp_path / "fx/skip.py").write_text("import os\nos.getenv('BB')")
    names = {e["name"] for e in scan_project.scan(tmp_path, ["fx/*"])["env_vars"]}
    assert names == {"AA"}


def test_cli(tmp_path, capsys):
    out = tmp_path / "scan.json"
    assert scan_project.main([str(FIXTURES / "fastapi-service"), "--out", str(out)]) == 0
    assert json.loads(out.read_text())["project"]["name"] == "ledgerline"
    assert json.loads(capsys.readouterr().out)["name"] == "ledgerline"
    assert scan_project.main([str(tmp_path / "missing")]) == 2


def test_idempotent(tmp_path):
    out = tmp_path / "scan.json"
    scan_project.main([str(FIXTURES / "react-tailwind-app"), "--out", str(out)])
    first = out.read_text()
    scan_project.main([str(FIXTURES / "react-tailwind-app"), "--out", str(out)])
    assert out.read_text() == first


def test_env_vars_in_tests_ignored(tmp_path):
    (tmp_path / "app.py").write_text("import os\nos.getenv('REAL_VAR')")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests/test_app.py").write_text("import os\nos.environ['FAKE_VAR'] = '1'")
    assert {e["name"] for e in scan_project.scan(tmp_path)["env_vars"]} == {"REAL_VAR"}
