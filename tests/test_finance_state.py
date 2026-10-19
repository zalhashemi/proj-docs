"""finance.py math and state.py update tracking (Phase 3)."""
import datetime as dt
import json

import pytest
import yaml

import finance
import scan_project
import state
from conftest import FIXTURES

TODAY = dt.date(2026, 10, 18)
INPUTS = {
    "currency": "EUR", "forecast_start": "2027-01", "starting_users": 1000,
    "monthly_growth_pct": "5-10", "infra_cost_per_user": 0.1, "fixed_infra_cost": 200,
    "revenue_model": "subscription", "arpu": 10, "paid_conversion_pct": "2-4",
    "budget_start": "2027-01", "contingency_pct": 10,
    "team_roles": ["Backend dev, 100%, 8000", {"role": "Designer", "allocation": 50, "rate": 6000}],
    "tooling_costs": ["Sentry, 26"], "one_time_costs": ["Audit, 5000, 2027-05", "Logo, 1000"],
}


# ---------------------------------------------------------------- finance

def test_forecast_math():
    f = finance.compute_forecast(INPUTS, TODAY)
    base = f["scenarios"]["Base"]
    assert f["months"][0] == "Jan 2027" and f["months"][-1] == "Dec 2027"
    assert base["growth_pct"] == 7.5 and base["conversion_pct"] == 3
    assert base["users"][0] == 1000
    assert base["users_m12"] == pytest.approx(1000 * 1.075 ** 11)
    assert base["cost"][0] == pytest.approx(200 + 1000 * 0.1)
    assert base["revenue"][0] == pytest.approx(1000 * 0.03 * 10)
    c, o = f["scenarios"]["Conservative"], f["scenarios"]["Optimistic"]
    assert c["users_m12"] < base["users_m12"] < o["users_m12"]
    assert not [s for s in f["inputs"] if s[3]]  # nothing assumed


def test_forecast_unknowns_become_assumptions():
    f = finance.compute_forecast({"starting_users": "unknown", "revenue_model": "none"}, TODAY)
    assumed = {k for k, _, _, a in f["inputs"] if a}
    assert {"starting_users", "monthly_growth_pct", "infra_cost_per_user"} <= assumed
    assert f["start"] == "2026-11"            # "next month"
    md = finance.render_forecast(f, {"users": "u.png", "cost": "c.png"})
    assert "⟨assumption⟩" in md and "No revenue model" in md and "not financial advice" in md
    assert "Net (revenue" not in md


def test_budget_math():
    b = finance.compute_budget(INPUTS, TODAY)
    monthly = 8000 + 0.5 * 6000 + 26 + 200   # team + tooling + fixed infra
    assert b["monthly_recurring"] == pytest.approx(monthly)
    q1, q2 = b["quarters"][0], b["quarters"][1]
    assert q1["one_time"] == 1000 and q2["one_time"] == 5000      # unspecified -> Q1, May -> Q2
    assert q1["contingency"] == pytest.approx((3 * monthly + 1000) * 0.10)
    assert b["year"]["total"] == pytest.approx(sum(q["total"] for q in b["quarters"]))
    assert b["year"]["total"] == pytest.approx((12 * monthly + 6000) * 1.10)
    md = finance.render_budget(b, {"quarters": "q.png"})
    assert "Q1 ⟨assumption⟩" in md and "| **Year** |" in md


def test_budget_without_team_does_not_invent_one():
    b = finance.compute_budget({"team_roles": "unknown"}, TODAY)
    assert b["team"] == [] and b["monthly_recurring"] == 0
    assert "No team roles" in finance.render_budget(b, {"quarters": "q.png"})


def test_span_parsing():
    assert finance.span("3-10") == (3, 6.5, 10)
    assert finance.span("5%") == (5, 5, 5)
    assert finance.span("10 to 4") == (4, 7, 10)


def test_finance_cli_writes_charts(tmp_path, capsys):
    pytest.importorskip("matplotlib")
    pd = tmp_path / "docs" / ".project-docs"
    pd.mkdir(parents=True)
    (pd / "inputs.yaml").write_text(yaml.safe_dump(INPUTS))
    assert finance.main(["forecast", "--inputs", str(pd / "inputs.yaml"), "--today", "2026-10-18"]) == 0
    md = capsys.readouterr().out
    assert "](.project-docs/assets/forecast-users.png)" in md
    assert (pd / "assets" / "forecast-revenue.png").is_file()
    assert finance.main(["budget", "--inputs", str(pd / "inputs.yaml"), "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["currency"] == "EUR"
    (pd / "bad.yaml").write_text("starting_users: lots\n")
    assert finance.main(["forecast", "--inputs", str(pd / "bad.yaml")]) == 1


# ---------------------------------------------------------------- state

def pack_md(pack, chapters):
    head = f"---\ntitle: X\nversion: 1.0.0\ndate: 2026-01-01\npack: {pack}\nchapters: [{', '.join(chapters)}]\n---\n\n"
    return head + "".join(f"# {c} {{#ch-{c}}}\n\n## A\n\n" for c in chapters)


@pytest.fixture
def project(fixture_copy):
    root = fixture_copy("fastapi-service")
    docs = root / "docs"
    (docs / ".project-docs").mkdir(parents=True)
    (docs / "developer.md").write_text(pack_md("developer", ["dev-guide", "api-reference", "data-model"]))
    (docs / "business.md").write_text(pack_md("business", ["project-brief"]))
    scan_project.main([str(root), "--out", str(docs / ".project-docs/scan.json")])
    assert state.main(["--docs-dir", str(docs), "set-stage", "complete"]) == 0
    assert state.main(["--docs-dir", str(docs), "record"]) == 0
    return root


def diff(root, capsys):
    capsys.readouterr()
    state.main(["--docs-dir", str(root / "docs"), "diff"])
    return json.loads(capsys.readouterr().out)


def rescan(root):
    scan_project.main([str(root), "--out", str(root / "docs/.project-docs/scan.json")])


def test_no_changes(project, capsys):
    d = diff(project, capsys)
    assert d["changed"] == [] and d["unchanged"] == 2


def test_packs_skip_chapters_without_evidence(project, fixture_copy, capsys):
    capsys.readouterr()
    state.main(["--docs-dir", str(project / "docs"), "packs"])
    p = json.loads(capsys.readouterr().out)
    assert {"api-reference", "data-model"} <= set(p["developer"]["chapters"])   # routes and DB found
    assert "backup-dr" in p["ops"]["chapters"]
    assert "forecast-1yr" in p["business"]["chapters"]                         # no `needs`: input-driven
    spa = fixture_copy("react-tailwind-app")                                    # no backend
    scan_project.main([str(spa), "--out", str(spa / "docs/.project-docs/scan.json")])
    capsys.readouterr()
    state.main(["--docs-dir", str(spa / "docs"), "packs"])
    p = json.loads(capsys.readouterr().out)
    assert p["developer"]["skipped"]["data-model"] == "no database found"
    assert p["developer"]["skipped"]["api-reference"] == "no openapi or routes found"
    assert "backup-dr" in p["ops"]["skipped"]


def test_has_evidence():
    assert not state.has_evidence({"models": [], "migrations": [], "engines": []})
    assert state.has_evidence({"models": [], "engines": ["postgres"]})
    assert not state.has_evidence([]) and state.has_evidence([{"x": 1}])


def test_new_route_flags_only_api_reference_chapter(project, capsys):
    orders = project / "app/routers/orders.py"
    orders.write_text(orders.read_text() + '\n\n@router.patch("/{order_id}")\ndef update(order_id: int):\n    pass\n')
    rescan(project)
    d = diff(project, capsys)
    assert [c["pack"] for c in d["changed"]] == ["developer"]
    c = d["changed"][0]
    assert c["hand_edited"] is False and c["needs_patch"] is True
    included = [ch for ch in c["chapters"] if ch["included"]]
    assert [ch["chapter"] for ch in included] == ["api-reference"]
    assert included[0]["keys"] == ["routes"] and included[0]["summary"] == ["route PATCH /orders/{order_id} added"]
    # integration-guide was left out but its evidence (routes) changed: offered, not included
    assert {ch["chapter"] for ch in c["chapters"] if not ch["included"]} == {"integration-guide"}


def test_new_script_and_env_var_flag_dev_guide(project, capsys):
    mk = project / "Makefile"
    mk.write_text(mk.read_text() + "\nformat:\n\truff format .\n")
    (project / ".env.example").write_text((project / ".env.example").read_text() + "REDIS_URL=\n")
    rescan(project)
    d = diff(project, capsys)
    ch = {c["chapter"]: c for c in d["changed"][0]["chapters"]}
    assert "script format added" in ch["dev-guide"]["summary"] and "env var REDIS_URL added" in ch["dev-guide"]["summary"]
    assert "api-reference" not in ch


def test_hand_edit_reported_not_overwritten(project, capsys):
    md = project / "docs/developer.md"
    md.write_text(md.read_text() + "\nMy own note.\n")
    d = diff(project, capsys)
    c = next(c for c in d["changed"] if c["pack"] == "developer")
    assert c["hand_edited"] is True and c["needs_patch"] is False
    assert "My own note." in md.read_text()


def test_record_rejects_chapter_from_other_pack(project):
    (project / "docs/ops.md").write_text(pack_md("ops", ["runbook", "prd"]))
    with pytest.raises(SystemExit, match="not in pack"):
        state.main(["--docs-dir", str(project / "docs"), "record", "--pack", "ops"])


def test_bump_and_rerecord(project, capsys):
    capsys.readouterr()
    state.main(["--docs-dir", str(project / "docs"), "bump", "developer"])
    out = json.loads(capsys.readouterr().out)
    assert out["version"] == ["1.0.0", "1.0.1"]
    text = (project / "docs/developer.md").read_text()
    assert "version: 1.0.1" in text and "## A" in text
    state.main(["--docs-dir", str(project / "docs"), "record", "--pack", "developer"])
    assert diff(project, capsys)["changed"] == []


def test_stage_suggestion(project, capsys):
    state.main(["--docs-dir", str(project / "docs"), "set-stage", "planning"])
    assert "stage_suggestion" in diff(project, capsys)


def test_diff_without_state(tmp_path, capsys):
    assert state.main(["--docs-dir", str(tmp_path), "diff"]) == 1
