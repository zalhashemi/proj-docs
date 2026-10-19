#!/usr/bin/env python3
"""Compute the 1-year forecast and the budget/resource plan from inputs.yaml.

All arithmetic happens here so the documents never contain hand-calculated numbers.
Prints Markdown (inputs table -> formulas -> outputs, plus chart image links) to paste into
docs/forecast-1yr.md or docs/budget-resources.md. Inputs that are missing or "unknown" fall
back to a stated default and are flagged as assumptions.

Usage:
  finance.py forecast --inputs docs/.project-docs/inputs.yaml [--theme theme.json] [--json]
  finance.py budget   --inputs docs/.project-docs/inputs.yaml [--theme theme.json] [--json]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import SKILL_DIR, load_json  # noqa: E402

DISCLAIMER = "*Planning estimates only, not financial advice.*"
# Fallbacks used only when the user answered "unknown". Each is reported as an assumption.
FALLBACK = {"currency": "USD", "starting_users": 100, "monthly_growth_pct": "3-10",
            "infra_cost_per_user": 0.05, "fixed_infra_cost": 50, "revenue_model": "none",
            "arpu": 10, "paid_conversion_pct": "2-5", "contingency_pct": 15}
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


# ---------------------------------------------------------------- inputs

def unknown(v) -> bool:
    return v is None or (isinstance(v, str) and v.strip().lower() in ("", "unknown", "?", "n/a"))


def get(inputs: dict, key: str, sources: list) -> object:
    v = inputs.get(key)
    if unknown(v):
        sources.append((key, FALLBACK.get(key), "default", True))
        return FALLBACK.get(key)
    sources.append((key, v, "user", False))
    return v


def number(v) -> float:
    if isinstance(v, (int, float)):
        return float(v)
    m = re.search(r"-?[\d,]*\.?\d+", str(v))
    if not m:
        raise ValueError(f"not a number: {v!r}")
    return float(m.group().replace(",", ""))


def span(v) -> tuple[float, float, float]:
    """'3-10' -> (3, 6.5, 10); '5' -> (5, 5, 5). Percent signs ignored."""
    nums = [number(x) for x in re.split(r"\s*(?:-|–|to)\s*", str(v).replace("%", "").strip()) if x.strip()]
    lo, hi = (nums[0], nums[-1]) if nums else (0.0, 0.0)
    lo, hi = min(lo, hi), max(lo, hi)
    return lo, (lo + hi) / 2, hi


def start_month(v, today: dt.date) -> dt.date:
    if isinstance(v, (dt.date, dt.datetime)):
        return dt.date(v.year, v.month, 1)
    m = re.fullmatch(r"(\d{4})-(\d{1,2})", str(v or "").strip())
    if m:
        return dt.date(int(m.group(1)), int(m.group(2)), 1)
    nxt = today.replace(day=1) + dt.timedelta(days=32)  # "next month" or anything else
    return nxt.replace(day=1)


def month_labels(start: dt.date, n: int = 12) -> list[str]:
    out = []
    y, m = start.year, start.month
    for _ in range(n):
        out.append(f"{MONTHS[m - 1]} {y}")
        m, y = (1, y + 1) if m == 12 else (m + 1, y)
    return out


def items(v, sources: list, key: str) -> list[dict]:
    """Parse 'Name, amount[, extra]' strings or dicts into [{name, amount, extra}]."""
    if unknown(v) or v == []:
        sources.append((key, "none provided", "default", True))
        return []
    sources.append((key, f"{len(v) if isinstance(v, list) else 1} item(s)", "user", False))
    out = []
    for it in (v if isinstance(v, list) else [v]):
        if isinstance(it, dict):
            out.append(it)
            continue
        parts = [p.strip() for p in str(it).split(",")]
        out.append({"name": parts[0], "values": parts[1:]})
    return out


def money(v: float, cur: str) -> str:
    return f"{cur} {v:,.0f}"


def rng(lo: float, hi: float, cur: str | None = None) -> str:
    f = (lambda x: money(x, cur)) if cur else (lambda x: f"{x:,.0f}")
    return f(lo) if round(lo) == round(hi) else f"{f(lo)} – {f(hi)}"


def inputs_table(sources: list, caption: str) -> str:
    rows = ["| Input | Value | Source | Assumption |", "|---|---|---|---|"]
    for key, val, src, assumed in sources:
        rows.append(f"| `{key}` | {val} | {src} | {'⟨assumption⟩' if assumed else '-'} |")
    return f"{caption}\n\n" + "\n".join(rows)


# ---------------------------------------------------------------- charts

def chart(path: Path, labels: list[str], series: dict[str, list[float]], colors: list[str],
          ylabel: str, kind: str = "line") -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7.2, 3.0), dpi=160)
    x = range(len(labels))
    if kind == "line":
        for (name, ys), c in zip(series.items(), colors):
            ax.plot(x, ys, label=name, color=c, linewidth=2.0, marker="o", markersize=3)
    else:  # stacked bars
        bottom = [0.0] * len(labels)
        for (name, ys), c in zip(series.items(), colors):
            ax.bar(x, ys, bottom=bottom, label=name, color=c, width=0.55)
            bottom = [b + y for b, y in zip(bottom, ys)]
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, fontsize=7, rotation=0 if len(labels) <= 4 else 45, ha="center" if len(labels) <= 4 else "right")
    ax.set_ylabel(ylabel, fontsize=8)
    ax.tick_params(axis="y", labelsize=7)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", alpha=0.25)
    # The figure caption (image alt text) carries the title; legend sits above the plot area.
    ax.legend(fontsize=7, frameon=False, ncol=len(series), loc="lower right", bbox_to_anchor=(1, 1.0))
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)


def theme_colors(theme_path: Path | None) -> dict:
    path = theme_path if theme_path and theme_path.is_file() else SKILL_DIR / "themes" / "default.json"
    return load_json(path)["colors"]


# ---------------------------------------------------------------- forecast

def compute_forecast(inputs: dict, today: dt.date) -> dict:
    src: list = []
    cur = str(get(inputs, "currency", src))
    start = start_month(get(inputs, "forecast_start", src), today)
    users0 = number(get(inputs, "starting_users", src))
    g = span(get(inputs, "monthly_growth_pct", src))
    cpu = number(get(inputs, "infra_cost_per_user", src))
    fixed = number(get(inputs, "fixed_infra_cost", src))
    model = str(get(inputs, "revenue_model", src)).lower()
    has_rev = model not in ("none", "no", "false")
    arpu = number(get(inputs, "arpu", src)) if has_rev else 0.0
    conv = span(get(inputs, "paid_conversion_pct", src)) if has_rev else (0.0, 0.0, 0.0)
    if not has_rev:
        src = [s for s in src if s[0] not in ("arpu", "paid_conversion_pct")]
    scen = {}
    for i, name in enumerate(("Conservative", "Base", "Optimistic")):
        users = [users0 * (1 + g[i] / 100) ** m for m in range(12)]
        cost = [fixed + u * cpu for u in users]
        revenue = [u * conv[i] / 100 * arpu for u in users]
        scen[name] = {"growth_pct": g[i], "conversion_pct": conv[i], "users": users, "cost": cost,
                      "revenue": revenue, "users_m12": users[-1], "cost_total": sum(cost),
                      "revenue_total": sum(revenue), "net_total": sum(revenue) - sum(cost)}
    base_plus = users0 * (1 + (g[1] + 1) / 100) ** 11
    return {"currency": cur, "start": start.isoformat()[:7], "months": month_labels(start),
            "revenue_model": model, "has_revenue": has_rev, "inputs": src, "scenarios": scen,
            "sensitivity_users_per_pp": base_plus - scen["Base"]["users_m12"]}


def render_forecast(f: dict, charts: dict[str, str]) -> str:
    cur, s, months = f["currency"], f["scenarios"], f["months"]
    names = list(s)
    out = [DISCLAIMER, "", "## Assumptions", "",
           inputs_table(f["inputs"], f"Currency: **{cur}**. Period: **monthly, {months[0]} – {months[-1]}**."), "",
           "## Method", "", "```text",
           "users[m]   = starting_users × (1 + growth)^m          (m = 0..11)",
           "infra[m]   = fixed_infra_cost + users[m] × infra_cost_per_user"]
    if f["has_revenue"]:
        out += ["paying[m]  = users[m] × paid_conversion",
                "revenue[m] = paying[m] × arpu", "net        = Σ revenue − Σ infra"]
    out += ["```", "", "## Scenarios", "",
            "| Scenario | Growth / month | Conversion |", "|---|---|---|"]
    for n in names:
        conv = f"{s[n]['conversion_pct']:g}%" if f["has_revenue"] else "-"
        out.append(f"| {n} | {s[n]['growth_pct']:g}% | {conv} |")

    def table(metric: str, fmt) -> list[str]:
        rows = [f"| Month | {' | '.join(names)} |", "|---|" + "---:|" * len(names)]
        for m, label in enumerate(months):
            rows.append(f"| {label} | " + " | ".join(fmt(s[n][metric][m]) for n in names) + " |")
        return rows

    out += ["", "## Users and usage", "", f"![Active users by scenario]({charts['users']})", ""]
    out += table("users", lambda v: f"{v:,.0f}")
    out += ["", "## Infrastructure cost", "", f"![Monthly infrastructure cost ({cur})]({charts['cost']})", ""]
    out += table("cost", lambda v: money(v, cur))
    out += ["", "## Revenue", ""]
    if f["has_revenue"]:
        out += [f"![Monthly revenue ({cur})]({charts['revenue']})", ""]
        out += table("revenue", lambda v: money(v, cur))
    else:
        out.append("No revenue model was provided, so revenue is not projected.")
    lo, hi = s["Conservative"], s["Optimistic"]
    out += ["", "## Summary", "", "| Metric (year 1) | Conservative | Base | Optimistic | Range |",
            "|---|---:|---:|---:|---|"]
    for label, key, cur_ in (("Active users at month 12", "users_m12", None), ("Total infra cost", "cost_total", cur),
                             ("Total revenue", "revenue_total", cur), ("Net (revenue − infra)", "net_total", cur)):
        if key in ("revenue_total", "net_total") and not f["has_revenue"]:
            continue
        fmt = (lambda v: money(v, cur_)) if cur_ else (lambda v: f"{v:,.0f}")
        out.append(f"| {label} | " + " | ".join(fmt(s[n][key]) for n in names) +
                   f" | {rng(min(lo[key], hi[key]), max(lo[key], hi[key]), cur_)} |")
    out += ["", "## What would change this forecast", "",
            f"- Each extra percentage point of monthly growth adds about "
            f"**{f['sensitivity_users_per_pp']:,.0f}** users by month 12 (base scenario).",
            "- Infrastructure cost scales linearly with users; a cheaper tier or caching lowers `infra_cost_per_user`."]
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- budget

def compute_budget(inputs: dict, today: dt.date) -> dict:
    src: list = []
    cur = str(get(inputs, "currency", src))
    start = start_month(get(inputs, "budget_start", src), today)
    contingency = number(get(inputs, "contingency_pct", src))
    team = []
    for it in items(inputs.get("team_roles"), src, "team_roles"):
        if "values" in it:
            vals = it["values"]
            alloc, rate = (number(vals[0]), number(vals[1])) if len(vals) >= 2 else (100.0, number(vals[0]))
        else:
            alloc, rate = number(it.get("allocation", 100)), number(it["rate"])
        team.append({"name": it.get("name") or it.get("role"), "allocation_pct": alloc, "rate": rate,
                     "monthly": alloc / 100 * rate})
    recurring = [{"name": f"{t['name']} ({t['allocation_pct']:g}%)", "monthly": t["monthly"], "kind": "team"} for t in team]
    for it in items(inputs.get("tooling_costs"), src, "tooling_costs"):
        amt = number(it["values"][0]) if "values" in it else number(it["amount"])
        recurring.append({"name": it.get("name"), "monthly": amt, "kind": "tooling"})
    if not unknown(inputs.get("fixed_infra_cost")):
        recurring.append({"name": "Infrastructure (fixed)", "monthly": number(inputs["fixed_infra_cost"]), "kind": "infra"})
        src.append(("fixed_infra_cost", inputs["fixed_infra_cost"], "user", False))
    one_time = []
    for it in items(inputs.get("one_time_costs"), src, "one_time_costs"):
        vals = it.get("values", [it.get("amount"), it.get("month")])
        amt = number(vals[0])
        when = vals[1] if len(vals) > 1 and vals[1] else None
        q = 1
        if when and re.fullmatch(r"\d{4}-\d{1,2}", str(when)):
            d = start_month(when, today)
            q = min(4, max(1, ((d.year - start.year) * 12 + d.month - start.month) // 3 + 1))
        one_time.append({"name": it.get("name"), "amount": amt, "quarter": q, "quarter_assumed": when is None})
    monthly = sum(r["monthly"] for r in recurring)
    labels = month_labels(start)
    quarters = []
    for q in range(1, 5):
        rec = 3 * monthly
        once = sum(o["amount"] for o in one_time if o["quarter"] == q)
        cont = (rec + once) * contingency / 100
        quarters.append({"quarter": f"Q{q} ({labels[3 * q - 3]} – {labels[3 * q - 1]})", "recurring": rec,
                         "one_time": once, "contingency": cont, "total": rec + once + cont})
    total = {k: sum(q[k] for q in quarters) for k in ("recurring", "one_time", "contingency", "total")}
    return {"currency": cur, "start": start.isoformat()[:7], "contingency_pct": contingency, "inputs": src,
            "team": team, "recurring": recurring, "one_time": one_time, "monthly_recurring": monthly,
            "quarters": quarters, "year": total}


def render_budget(b: dict, charts: dict[str, str]) -> str:
    cur = b["currency"]
    m = lambda v: money(v, cur)
    out = [DISCLAIMER, "", "## Inputs", "",
           inputs_table(b["inputs"], f"Currency: **{cur}**. Period: **12 months from {b['start']}**, "
                                     f"contingency **{b['contingency_pct']:g}%**."), "", "## Team", ""]
    if b["team"]:
        out += ["| Role | Allocation | Monthly rate | Monthly cost | Annual cost |", "|---|---:|---:|---:|---:|"]
        out += [f"| {t['name']} | {t['allocation_pct']:g}% | {m(t['rate'])} | {m(t['monthly'])} | {m(12 * t['monthly'])} |"
                for t in b["team"]]
    else:
        out += ["> [!ASSUMPTION]", "> No team roles or rates were provided, so team cost is excluded from the totals."]
    out += ["", "## Infrastructure and tooling", ""]
    other = [r for r in b["recurring"] if r["kind"] != "team"]
    if other:
        out += ["| Item | Monthly | Annual |", "|---|---:|---:|"]
        out += [f"| {r['name']} | {m(r['monthly'])} | {m(12 * r['monthly'])} |" for r in other]
    else:
        out.append("No recurring infrastructure or tooling costs were provided.")
    out += ["", "## Licences and one-time costs", ""]
    if b["one_time"]:
        out += ["| Item | Amount | Quarter |", "|---|---:|---|"]
        out += [f"| {o['name']} | {m(o['amount'])} | Q{o['quarter']}{' ⟨assumption⟩' if o['quarter_assumed'] else ''} |"
                for o in b["one_time"]]
    else:
        out.append("No one-time costs were provided.")
    out += ["", "## Totals by quarter", "", f"![Budget by quarter ({cur})]({charts['quarters']})", "",
            "| Quarter | Recurring | One-time | Contingency | Total |", "|---|---:|---:|---:|---:|"]
    for q in b["quarters"]:
        out.append(f"| {q['quarter']} | {m(q['recurring'])} | {m(q['one_time'])} | {m(q['contingency'])} | {m(q['total'])} |")
    y = b["year"]
    out.append(f"| **Year** | **{m(y['recurring'])}** | **{m(y['one_time'])}** | **{m(y['contingency'])}** | **{m(y['total'])}** |")
    out += ["", "## Formulas", "", "```text",
            "team_monthly[r]   = allocation[r] × monthly_rate[r]",
            "recurring_monthly = Σ team_monthly + Σ tooling + fixed_infra",
            "recurring[q]      = 3 × recurring_monthly",
            "contingency[q]    = (recurring[q] + one_time[q]) × contingency_pct",
            "total[q]          = recurring[q] + one_time[q] + contingency[q]",
            "```", "", f"One-time costs without a month are placed in Q1 ⟨assumption⟩."]
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- CLI

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__.split("\n\n", 1)[1])
    ap.add_argument("kind", choices=["forecast", "budget"])
    ap.add_argument("--inputs", type=Path, required=True, help="inputs.yaml with the user's answers")
    ap.add_argument("--theme", type=Path, help="theme.json for chart colours")
    ap.add_argument("--assets", type=Path, help="chart output dir (default <inputs dir>/assets)")
    ap.add_argument("--md-dir", type=Path, help="dir of the doc that embeds the charts (default: docs/)")
    ap.add_argument("--today", help="YYYY-MM-DD, for reproducible 'next month' starts")
    ap.add_argument("--json", action="store_true", help="print computed numbers as JSON instead of Markdown")
    args = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to cp1252
    if not args.inputs.is_file():
        print(json.dumps({"error": f"inputs file not found: {args.inputs}"}), file=sys.stderr)
        return 2
    import yaml
    inputs = yaml.safe_load(args.inputs.read_text(encoding="utf-8")) or {}
    today = dt.date.fromisoformat(args.today) if args.today else dt.date.today()
    assets = args.assets or args.inputs.parent / "assets"
    md_dir = args.md_dir or args.inputs.parent.parent
    rel = lambda p: Path(os.path.relpath(p, md_dir)).as_posix()
    colors = theme_colors(args.theme)
    trio = [colors["muted"], colors["primary"], colors["accent"]]
    try:
        if args.kind == "forecast":
            data = compute_forecast(inputs, today)
            charts = {}
            for metric, ylabel in (("users", "users"), ("cost", data["currency"]), ("revenue", data["currency"])):
                if metric == "revenue" and not data["has_revenue"]:
                    continue
                path = assets / f"forecast-{metric}.png"
                chart(path, data["months"],
                      {n: s[metric] for n, s in data["scenarios"].items()}, trio, ylabel)
                charts[metric] = rel(path)
            text = render_forecast(data, charts)
        else:
            data = compute_budget(inputs, today)
            path = assets / "budget-quarters.png"
            chart(path, [q["quarter"].split(" (")[0] for q in data["quarters"]],
                  {"Recurring": [q["recurring"] for q in data["quarters"]],
                   "One-time": [q["one_time"] for q in data["quarters"]],
                   "Contingency": [q["contingency"] for q in data["quarters"]]},
                  [colors["primary"], colors["accent"], colors["warning"]], data["currency"], kind="bar")
            text = render_budget(data, {"quarters": rel(path)})
    except (ValueError, KeyError, IndexError) as e:
        print(json.dumps({"error": f"bad input: {e}"}), file=sys.stderr)
        return 1
    print(json.dumps(data, indent=2, default=str) if args.json else text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
