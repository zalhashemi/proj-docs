#!/usr/bin/env python3
"""Track generated docs so updates touch only what changed.

state.json stores the lifecycle stage, the scan snapshot at generation time, and per doc:
a hash of the scan keys it depends on (catalog `scan_keys`), a hash of the Markdown as
generated (to detect hand edits), and its version.

Usage (run from the project root, or pass --docs-dir):
  state.py set-stage planning|complete
  state.py record [--doc ID ...]      after rendering: store hashes for these docs (default: all)
  state.py diff                       which docs need a patch, what changed, which were hand-edited
  state.py bump ID                    front matter: version x.y.z -> x.y.(z+1), date -> today
  state.py show
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import SKILL_DIR, load_json, write_json  # noqa: E402


def sha(value) -> str:
    data = value if isinstance(value, bytes) else json.dumps(value, sort_keys=True, default=str).encode()
    return hashlib.sha256(data).hexdigest()[:16]


def catalog() -> dict:
    import yaml
    return {d["id"]: d for d in yaml.safe_load((SKILL_DIR / "catalog.yaml").read_text(encoding="utf-8"))["docs"]}


class State:
    def __init__(self, docs_dir: Path):
        self.docs_dir = docs_dir
        self.dir = docs_dir / ".project-docs"
        self.path = self.dir / "state.json"
        self.data = load_json(self.path) if self.path.is_file() else {"version": 1, "stage": None, "docs": {}}

    def save(self) -> None:
        write_json(self.path, self.data)

    def scan(self) -> dict:
        p = self.dir / "scan.json"
        if not p.is_file():
            raise SystemExit(json.dumps({"error": f"{p} not found; run scan_project.py first"}))
        return load_json(p)


def front_matter_version(text: str) -> str | None:
    m = re.search(r"^version:\s*['\"]?([\w.]+)", text, re.M)
    return m.group(1) if m else None


def cmd_record(st: State, ids: list[str]) -> dict:
    cat, scan = catalog(), st.scan()
    ids = ids or sorted(p.stem for p in st.docs_dir.glob("*.md") if p.stem in cat)
    recorded = []
    for doc_id in ids:
        md = st.docs_dir / f"{doc_id}.md"
        if doc_id not in cat or not md.is_file():
            raise SystemExit(json.dumps({"error": f"cannot record '{doc_id}': unknown id or missing {md}"}))
        keys = cat[doc_id]["scan_keys"]
        st.data["docs"][doc_id] = {"scan_keys": keys, "scan_hash": sha({k: scan.get(k) for k in keys}),
                                   "md_hash": sha(md.read_bytes()),
                                   "version": front_matter_version(md.read_text(encoding="utf-8")),
                                   "recorded": dt.date.today().isoformat()}
        recorded.append(doc_id)
    st.data["scan_snapshot"] = scan
    st.data["scan_hash"] = sha(scan)
    st.save()
    return {"recorded": recorded}


# ---------------------------------------------------------------- change summaries

def _keyed(items, key):
    return {key(i): i for i in items or []}


def summarize(key: str, old, new) -> list[str]:
    """Human-readable differences for one scan key."""
    def diff_sets(label, a, b):
        out = [f"{label} {x} added" for x in sorted(b - a)]
        return out + [f"{label} {x} removed" for x in sorted(a - b)]
    if key == "routes":
        f = lambda rs: {f"{r['method']} {r['path']}" for r in rs or []}
        return diff_sets("route", f(old), f(new))
    if key == "openapi":
        f = lambda specs: {f"{o['method']} {o['path']}" for s in specs or [] for o in s.get("operations", [])}
        return diff_sets("operation", f(old), f(new))
    if key == "scripts":
        a, b = _keyed(old, lambda s: s["name"]), _keyed(new, lambda s: s["name"])
        out = diff_sets("script", set(a), set(b))
        return out + [f"script {n} changed" for n in sorted(set(a) & set(b)) if a[n]["command"] != b[n]["command"]]
    if key == "env_vars":
        return diff_sets("env var", {e["name"] for e in old or []}, {e["name"] for e in new or []})
    if key == "dependencies":
        flat = lambda deps: {f"{n}": v for d in deps or [] for part in ("runtime", "dev") for n, v in d[part].items()}
        a, b = flat(old), flat(new)
        out = diff_sets("dependency", set(a), set(b))
        return out + [f"dependency {n} {a[n]} -> {b[n]}" for n in sorted(set(a) & set(b)) if a[n] != b[n]]
    if key == "database":
        f = lambda d: {m["name"] for m in (d or {}).get("models", [])}
        out = diff_sets("model", f(old), f(new))
        mig = lambda d: sum(m["count"] for m in (d or {}).get("migrations", []))
        if mig(old) != mig(new):
            out.append(f"migrations {mig(old)} -> {mig(new)}")
        return out or ["database config changed"]
    if key == "third_party":
        return diff_sets("service", {t["service"] for t in old or []}, {t["service"] for t in new or []})
    if key == "ci":
        f = lambda cs: {f"{c['file']}:{j}" for c in cs or [] for j in c.get("jobs", [])} | {c["file"] for c in cs or []}
        return diff_sets("CI", f(old), f(new)) or ["CI config changed"]
    if key == "git":
        o, n = old or {}, new or {}
        out = [f"new tag {t['name']}" for t in n.get("tags", []) if t not in o.get("tags", [])]
        if n.get("commits", 0) != o.get("commits", 0):
            out.append(f"{n.get('commits', 0) - o.get('commits', 0):+d} commits")
        return out or ["git metadata changed"]
    if key == "tests":
        o, n = old or {}, new or {}
        return [f"test files {o.get('files')} -> {n.get('files')}, cases ~{o.get('cases_approx')} -> ~{n.get('cases_approx')}"]
    return [f"{key} changed"]


def cmd_diff(st: State) -> dict:
    scan, old_scan = st.scan(), st.data.get("scan_snapshot", {})
    cat = catalog()
    changed, unchanged, missing = [], 0, []
    for doc_id, rec in sorted(st.data["docs"].items()):
        md = st.docs_dir / f"{doc_id}.md"
        if not md.is_file():
            missing.append(doc_id)
            continue
        keys = cat.get(doc_id, {}).get("scan_keys", rec["scan_keys"])
        hand_edited = sha(md.read_bytes()) != rec["md_hash"]
        stale = [k for k in keys if sha(scan.get(k)) != sha(old_scan.get(k))]
        if not stale and not hand_edited:
            unchanged += 1
            continue
        summary = [s for k in stale for s in summarize(k, old_scan.get(k), scan.get(k))]
        if stale or hand_edited:
            changed.append({"doc": doc_id, "keys": stale, "summary": summary, "hand_edited": hand_edited,
                            "needs_patch": bool(stale)})
    untracked = sorted(p.stem for p in st.docs_dir.glob("*.md") if p.stem in cat and p.stem not in st.data["docs"])
    out = {"stage": st.data.get("stage"), "changed": changed, "unchanged": unchanged,
           "missing_markdown": missing, "untracked": untracked}
    if st.data.get("stage") == "planning" and scan.get("stage_hint") == "active":
        out["stage_suggestion"] = "The project now has code; ask whether it is complete and the full catalog should be offered."
    return out


def cmd_bump(st: State, doc_id: str) -> dict:
    md = st.docs_dir / f"{doc_id}.md"
    if not md.is_file():
        raise SystemExit(json.dumps({"error": f"{md} not found"}))
    text = md.read_text(encoding="utf-8")
    old = front_matter_version(text) or "1.0.0"
    parts = (old.split(".") + ["0", "0"])[:3]
    new = ".".join(parts[:2] + [str(int(parts[2]) + 1 if parts[2].isdigit() else 1)])
    today = dt.date.today().isoformat()
    head, sep, body = text.partition("\n---")  # only touch the front matter block
    head = re.sub(r"^version:.*$", f"version: {new}", head, count=1, flags=re.M)
    head = re.sub(r"^date:.*$", f'date: "{today}"', head, count=1, flags=re.M)
    md.write_text(head + sep + body, encoding="utf-8")
    return {"doc": doc_id, "version": [old, new], "date": today}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__.split("\n\n", 1)[1])
    ap.add_argument("--docs-dir", type=Path, default=Path("docs"))
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("set-stage")
    s.add_argument("stage", choices=["planning", "complete"])
    r = sub.add_parser("record")
    r.add_argument("--doc", action="append", default=[])
    sub.add_parser("diff")
    b = sub.add_parser("bump")
    b.add_argument("doc")
    sub.add_parser("show")
    args = ap.parse_args(argv)
    st = State(args.docs_dir)
    if args.cmd == "set-stage":
        st.data["stage"] = args.stage
        st.save()
        result = {"stage": args.stage}
    elif args.cmd == "record":
        result = cmd_record(st, args.doc)
    elif args.cmd == "diff":
        if not st.path.is_file():
            result = {"error": "no state.json yet: this is a first run"}
            print(json.dumps(result, indent=2))
            return 1
        result = cmd_diff(st)
    elif args.cmd == "bump":
        result = cmd_bump(st, args.doc)
    else:
        result = {k: v for k, v in st.data.items() if k != "scan_snapshot"}
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
