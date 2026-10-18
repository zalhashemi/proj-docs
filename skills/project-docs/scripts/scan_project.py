#!/usr/bin/env python3
"""Summarise a project into scan.json for the project-docs skill.

Stdlib-first and read-only. Respects .gitignore, skips vendored/build dirs and binaries,
caps bytes read per file. Missing git, empty repos and unknown stacks degrade gracefully.

Usage: scan_project.py <project> [--out docs/.project-docs/scan.json] [--exclude GLOB ...]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import git, list_files, read_text, write_json  # noqa: E402

try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None
try:
    import yaml
except ImportError:
    yaml = None

LANG_EXT = {".py": "Python", ".js": "JavaScript", ".jsx": "JavaScript", ".mjs": "JavaScript",
            ".cjs": "JavaScript", ".ts": "TypeScript", ".tsx": "TypeScript", ".go": "Go",
            ".rs": "Rust", ".java": "Java", ".kt": "Kotlin", ".swift": "Swift", ".dart": "Dart",
            ".rb": "Ruby", ".php": "PHP", ".cs": "C#", ".c": "C", ".h": "C", ".cpp": "C++",
            ".hpp": "C++", ".scala": "Scala", ".vue": "Vue", ".svelte": "Svelte", ".ex": "Elixir",
            ".exs": "Elixir", ".sql": "SQL", ".sh": "Shell", ".ipynb": "Jupyter",
            ".html": "HTML", ".css": "CSS", ".scss": "SCSS"}
CODE_LANGS = set(LANG_EXT.values()) - {"HTML", "CSS", "SCSS", "SQL", "Shell"}

# dependency name (prefix match for scoped) -> framework label
FRAMEWORKS = {"react": "React", "next": "Next.js", "vue": "Vue", "nuxt": "Nuxt", "svelte": "Svelte",
              "@sveltejs/kit": "SvelteKit", "@angular/core": "Angular", "solid-js": "Solid",
              "express": "Express", "fastify": "Fastify", "@nestjs/core": "NestJS", "koa": "Koa",
              "hono": "Hono", "fastapi": "FastAPI", "flask": "Flask", "django": "Django",
              "rails": "Rails", "sinatra": "Sinatra", "laravel/framework": "Laravel",
              "spring-boot": "Spring Boot", "org.springframework.boot": "Spring Boot",
              "github.com/gin-gonic/gin": "Gin", "github.com/labstack/echo": "Echo",
              "github.com/gofiber/fiber": "Fiber", "github.com/spf13/cobra": "Cobra",
              "actix-web": "Actix", "axum": "Axum", "clap": "clap", "flutter": "Flutter",
              "react-native": "React Native", "expo": "Expo", "electron": "Electron",
              "tailwindcss": "Tailwind CSS", "@mui/material": "MUI", "@chakra-ui/react": "Chakra UI",
              "@mantine/core": "Mantine", "antd": "Ant Design", "prisma": "Prisma",
              "@prisma/client": "Prisma", "typeorm": "TypeORM", "sequelize": "Sequelize",
              "sqlalchemy": "SQLAlchemy", "alembic": "Alembic", "pydantic": "Pydantic",
              "click": "Click", "typer": "Typer", "commander": "Commander", "yargs": "yargs",
              "torch": "PyTorch", "tensorflow": "TensorFlow", "scikit-learn": "scikit-learn",
              "pandas": "pandas", "vite": "Vite", "streamlit": "Streamlit", "gradio": "Gradio"}
FRONTEND = {"React", "Next.js", "Vue", "Nuxt", "Svelte", "SvelteKit", "Angular", "Solid",
            "Electron", "Streamlit", "Gradio"}
MOBILE = {"Flutter", "React Native", "Expo"}
BACKEND = {"Express", "Fastify", "NestJS", "Koa", "Hono", "FastAPI", "Flask", "Django", "Rails",
           "Sinatra", "Laravel", "Spring Boot", "Gin", "Echo", "Fiber", "Actix", "Axum"}
CLI = {"Click", "Typer", "Commander", "yargs", "Cobra", "clap"}
ML = {"PyTorch", "TensorFlow", "scikit-learn", "pandas"}

THIRD_PARTY = {  # dependency substring or env prefix -> service
    "stripe": "Stripe", "sentry": "Sentry", "aws-sdk": "AWS", "@aws-sdk": "AWS", "boto3": "AWS",
    "firebase": "Firebase", "@google-cloud": "Google Cloud", "google-cloud": "Google Cloud",
    "twilio": "Twilio", "sendgrid": "SendGrid", "mailgun": "Mailgun", "postmark": "Postmark",
    "resend": "Resend", "openai": "OpenAI", "anthropic": "Anthropic", "auth0": "Auth0",
    "@clerk": "Clerk", "supabase": "Supabase", "redis": "Redis", "ioredis": "Redis",
    "posthog": "PostHog", "segment": "Segment", "mixpanel": "Mixpanel", "datadog": "Datadog",
    "dd-trace": "Datadog", "newrelic": "New Relic", "algolia": "Algolia",
    "cloudinary": "Cloudinary", "@slack": "Slack", "slack-sdk": "Slack", "paypal": "PayPal",
    "pusher": "Pusher", "launchdarkly": "LaunchDarkly", "@vercel": "Vercel",
    "opentelemetry": "OpenTelemetry", "elasticsearch": "Elasticsearch", "mongodb": "MongoDB",
    "mongoose": "MongoDB", "kafka": "Kafka", "rabbitmq": "RabbitMQ", "amqplib": "RabbitMQ",
    "github": "GitHub", "google_fonts": "Google Fonts"}
ENV_SERVICE = {"STRIPE_": "Stripe", "SENTRY_": "Sentry", "AWS_": "AWS", "S3_": "AWS",
               "TWILIO_": "Twilio", "SENDGRID_": "SendGrid", "OPENAI_": "OpenAI",
               "ANTHROPIC_": "Anthropic", "AUTH0_": "Auth0", "CLERK_": "Clerk",
               "SUPABASE_": "Supabase", "REDIS_": "Redis", "POSTHOG_": "PostHog",
               "FIREBASE_": "Firebase", "DD_": "Datadog", "SLACK_": "Slack", "GOOGLE_": "Google Cloud",
               "MAILGUN_": "Mailgun", "ALGOLIA_": "Algolia"}

ENV_CODE_PATTERNS = [
    r"process\.env\.([A-Z][A-Z0-9_]+)", r"process\.env\[['\"]([A-Z][A-Z0-9_]+)['\"]\]",
    r"import\.meta\.env\.([A-Z][A-Z0-9_]+)",
    r"os\.environ\[['\"]([A-Z][A-Z0-9_]+)['\"]\]",
    r"os\.(?:environ\.get|getenv)\(\s*['\"]([A-Z][A-Z0-9_]+)['\"]",
    r"ENV\[['\"]([A-Z][A-Z0-9_]+)['\"]\]", r"ENV\.fetch\(['\"]([A-Z][A-Z0-9_]+)['\"]",
    r"System\.getenv\(\"([A-Z][A-Z0-9_]+)\"\)", r"os\.Getenv\(\"([A-Z][A-Z0-9_]+)\"\)",
    r"env::var\(\"([A-Z][A-Z0-9_]+)\"\)", r"Platform\.environment\[['\"]([A-Z][A-Z0-9_]+)['\"]\]",
    r"getenv\(['\"]([A-Z][A-Z0-9_]+)['\"]\)",
]
ENV_RE = re.compile("|".join(ENV_CODE_PATTERNS))
HTTP = "get|post|put|patch|delete|head|options"
ROUTE_PATTERNS = [  # (framework, regex, method group, path group, confidence)
    ("Express/Fastify", re.compile(rf"\b(?:app|router|server|fastify|api|r)\.({HTTP})\(\s*['\"`](/[^'\"`]*)['\"`]"), 1, 2, "medium"),
    ("FastAPI/Flask", re.compile(rf"@\w+\.({HTTP})\(\s*['\"]([^'\"]*)['\"]"), 1, 2, "medium"),
    ("Flask", re.compile(r"@\w+\.route\(\s*['\"]([^'\"]+)['\"](?:.*?methods\s*=\s*\[([^\]]+)\])?"), 2, 1, "medium"),
    ("Spring", re.compile(r"@(Get|Post|Put|Patch|Delete|Request)Mapping\(\s*(?:value\s*=\s*|path\s*=\s*)?\"([^\"]+)\""), 1, 2, "medium"),
    ("Gin/Echo", re.compile(r"\.\s*(GET|POST|PUT|PATCH|DELETE)\(\s*\"(/[^\"]*)\""), 1, 2, "medium"),
]
TEST_FILE = re.compile(r"(^|/)(test_[^/]+\.py|[^/]+_test\.(py|go|dart)|[^/]+\.(test|spec)\.[jt]sx?|"
                       r"[^/]+_spec\.rb|[^/]+Tests?\.(java|kt|swift|cs))$")
TEST_CASE = re.compile(r"^\s*(?:def test_|async def test_|func Test|it\(|test\(|it ['\"]|"
                       r"testWidgets\(|@Test)", re.M)


def is_test(f: str) -> bool:
    return bool(TEST_FILE.search(f)) or any(
        x in ("test", "tests", "__tests__", "spec", "e2e") for x in f.split("/")[:-1])


def _toml(text: str) -> dict:
    if tomllib is None:
        return {}
    try:
        return tomllib.loads(text)
    except Exception:
        return {}


def _yaml(text: str):
    if yaml is None:
        return None
    try:
        return yaml.safe_load(text)
    except Exception:
        return None


def _json(text: str) -> dict:
    try:
        data = json.loads(text)
        return data if isinstance(data, dict) else {}
    except ValueError:
        return {}


def _req_name(spec: str) -> str:
    return re.split(r"[\s<>=!~\[;@(]", spec.strip(), 1)[0].lower()


class Scanner:
    def __init__(self, root: Path, excludes: list[str]):
        self.root = root
        self.files = list_files(root, excludes)
        self.fileset = set(self.files)
        self._cache: dict[str, str] = {}

    def text(self, rel: str) -> str:
        if rel not in self._cache:
            self._cache[rel] = read_text(self.root / rel)
        return self._cache[rel]

    def glob(self, pattern: str) -> list[str]:
        return [f for f in self.files if PurePosixPath(f).match(pattern)]

    def named(self, *names: str) -> list[str]:
        return [f for f in self.files if PurePosixPath(f).name in names]

    # ------------------------------------------------------------ manifests
    def manifests(self) -> tuple[list[dict], dict]:
        deps, meta = [], {}
        for f in self.named("package.json"):
            d = _json(self.text(f))
            deps.append({"ecosystem": "npm", "manifest": f, "name": d.get("name"),
                         "runtime": d.get("dependencies", {}) or {},
                         "dev": d.get("devDependencies", {}) or {}})
            if "/" not in f:
                meta.update(name=d.get("name"), version=d.get("version"),
                            description=d.get("description"), license=d.get("license"))
                meta["_pkg"] = d
        for f in self.named("pyproject.toml"):
            d = _toml(self.text(f))
            proj, poetry = d.get("project", {}), d.get("tool", {}).get("poetry", {})
            rt = {_req_name(s): s for s in proj.get("dependencies", [])}
            rt.update({k.lower(): str(v) for k, v in poetry.get("dependencies", {}).items()
                       if k.lower() != "python"})
            dev = {}
            for group in proj.get("optional-dependencies", {}).values():
                dev.update({_req_name(s): s for s in group})
            for group in d.get("dependency-groups", {}).values():
                dev.update({_req_name(s): s for s in group if isinstance(s, str)})
            deps.append({"ecosystem": "pip", "manifest": f, "name": proj.get("name") or poetry.get("name"),
                         "runtime": rt, "dev": dev})
            if "/" not in f:
                meta.setdefault("name", proj.get("name") or poetry.get("name"))
                meta.setdefault("version", proj.get("version") or poetry.get("version"))
                meta.setdefault("description", proj.get("description") or poetry.get("description"))
                meta["_pyproject"] = d
        for f in self.glob("*requirements*.txt"):
            lines = [l for l in self.text(f).splitlines() if l.strip() and not l.startswith(("#", "-"))]
            target = "dev" if "dev" in f or "test" in f else "runtime"
            entry = {"ecosystem": "pip", "manifest": f, "runtime": {}, "dev": {}}
            entry[target] = {_req_name(l): l.strip() for l in lines}
            deps.append(entry)
        for f in self.named("go.mod"):
            t = self.text(f)
            mod = re.search(r"^module\s+(\S+)", t, re.M)
            req = dict(re.findall(r"^\s*([\w./-]+\.[\w./-]+)\s+(v[\w.+-]+)", t, re.M))
            deps.append({"ecosystem": "go", "manifest": f, "name": mod and mod.group(1),
                         "runtime": req, "dev": {}})
            meta.setdefault("name", mod and mod.group(1).split("/")[-1])
        for f in self.named("Cargo.toml"):
            d = _toml(self.text(f))
            norm = lambda x: {k: (v if isinstance(v, str) else v.get("version", "*") if isinstance(v, dict) else str(v))
                              for k, v in x.items()}
            deps.append({"ecosystem": "cargo", "manifest": f, "name": d.get("package", {}).get("name"),
                         "runtime": norm(d.get("dependencies", {})), "dev": norm(d.get("dev-dependencies", {}))})
            meta.setdefault("name", d.get("package", {}).get("name"))
        for f in self.named("pom.xml"):
            t = self.text(f)
            arts = re.findall(r"<dependency>\s*<groupId>([^<]+)</groupId>\s*<artifactId>([^<]+)</artifactId>"
                              r"(?:\s*<version>([^<]+)</version>)?", t)
            deps.append({"ecosystem": "maven", "manifest": f, "runtime": {f"{g}:{a}": v or "" for g, a, v in arts},
                         "dev": {}})
        for f in self.glob("build.gradle*"):
            t = self.text(f)
            found = re.findall(r"(?:implementation|api|compileOnly|runtimeOnly|testImplementation)\s*\(?\s*['\"]([^'\"]+)['\"]", t)
            deps.append({"ecosystem": "gradle", "manifest": f,
                         "runtime": {":".join(x.split(":")[:2]): (x.split(":") + [""])[2] for x in found}, "dev": {}})
        for f in self.named("composer.json"):
            d = _json(self.text(f))
            deps.append({"ecosystem": "composer", "manifest": f, "runtime": d.get("require", {}),
                         "dev": d.get("require-dev", {})})
        for f in self.named("Gemfile"):
            gems = dict(re.findall(r"^\s*gem\s+['\"]([^'\"]+)['\"](?:\s*,\s*['\"]([^'\"]+)['\"])?", self.text(f), re.M))
            deps.append({"ecosystem": "rubygems", "manifest": f, "runtime": gems, "dev": {}})
        for f in self.named("pubspec.yaml"):
            d = _yaml(self.text(f)) or {}
            norm = lambda x: {k: (v if isinstance(v, str) else "sdk" if isinstance(v, dict) and "sdk" in v else str(v))
                              for k, v in (x or {}).items()}
            deps.append({"ecosystem": "pub", "manifest": f, "name": d.get("name"),
                         "runtime": norm(d.get("dependencies")), "dev": norm(d.get("dev_dependencies"))})
            if "/" not in f:
                meta.setdefault("name", d.get("name"))
                meta.setdefault("version", d.get("version"))
                meta.setdefault("description", d.get("description"))
        for f in self.glob("*.csproj"):
            refs = re.findall(r"<PackageReference\s+Include=\"([^\"]+)\"(?:\s+Version=\"([^\"]+)\")?", self.text(f))
            deps.append({"ecosystem": "nuget", "manifest": f, "runtime": dict(refs), "dev": {}})
        return deps, meta

    # ------------------------------------------------------------ sections
    def languages(self) -> dict:
        c = Counter(LANG_EXT[PurePosixPath(f).suffix] for f in self.files
                    if PurePosixPath(f).suffix in LANG_EXT)
        return dict(c.most_common())

    @staticmethod
    def frameworks(deps: list[dict]) -> list[str]:
        found = set()
        for d in deps:
            for name in list(d["runtime"]) + list(d["dev"]):
                n = name.lower()
                for key, label in FRAMEWORKS.items():
                    if n == key or n.startswith(key + ":") or (key.startswith("org.") and n.startswith(key)):
                        found.add(label)
            if d["ecosystem"] == "pub" and "flutter" in d["runtime"]:
                found.add("Flutter")
        return sorted(found)

    def packages(self, deps: list[dict]) -> list[dict]:
        manifests = {"package.json", "pyproject.toml", "go.mod", "Cargo.toml", "pubspec.yaml",
                     "composer.json", "pom.xml"}
        return [{"path": str(PurePosixPath(d["manifest"]).parent), "name": d.get("name"),
                 "ecosystem": d["ecosystem"]}
                for d in deps if "/" in d["manifest"] and PurePosixPath(d["manifest"]).name in manifests]

    def project_type(self, fw: list[str], packages: list[dict], meta: dict, langs: dict) -> dict:
        types, evidence = [], []
        pkg = meta.get("_pkg", {})
        if pkg.get("workspaces") or self.named("pnpm-workspace.yaml", "lerna.json", "nx.json", "turbo.json") \
                or len(packages) >= 2:
            types.append("monorepo")
            evidence.append(f"{len(packages)} sub-packages")
        if set(fw) & MOBILE or any(f.startswith(("android/", "ios/")) for f in self.files):
            types.append("mobile app")
            evidence.append("mobile framework: " + ", ".join(sorted(set(fw) & MOBILE)) or "android/ios dirs")
        if set(fw) & FRONTEND:
            types.append("web app")
            evidence.append("frontend: " + ", ".join(sorted(set(fw) & FRONTEND)))
        if set(fw) & BACKEND:
            types.append("API/service")
            evidence.append("backend: " + ", ".join(sorted(set(fw) & BACKEND)))
        scripts = meta.get("_pyproject", {}).get("project", {}).get("scripts")
        if set(fw) & CLI or pkg.get("bin") or scripts:
            types.append("CLI")
            evidence.append("CLI entry points")
        if set(fw) & ML or langs.get("Jupyter"):
            types.append("data/ML")
            evidence.append("ML/data libraries or notebooks")
        if not types:
            types.append("library" if langs else "unknown")
        return {"primary": types[0], "all": types, "evidence": evidence}

    def entry_points(self, meta: dict) -> list[dict]:
        eps = []
        pkg = meta.get("_pkg", {})
        if pkg.get("main"):
            eps.append({"kind": "npm main", "target": pkg["main"]})
        bins = pkg.get("bin")
        for name, target in (bins.items() if isinstance(bins, dict) else [(pkg.get("name"), bins)] if bins else []):
            eps.append({"kind": "npm bin", "name": name, "target": target})
        for name, target in meta.get("_pyproject", {}).get("project", {}).get("scripts", {}).items():
            eps.append({"kind": "console script", "name": name, "target": target})
        candidates = {"main.py", "app.py", "manage.py", "wsgi.py", "asgi.py", "main.go", "main.rs",
                      "main.dart", "index.js", "index.ts", "server.js", "server.ts", "main.ts",
                      "main.tsx", "App.tsx", "Program.cs", "Application.java"}
        for f in self.files:
            name = PurePosixPath(f).name
            if name in candidates and f.count("/") <= 3 and not is_test(f):
                eps.append({"kind": "file", "target": f})
            elif name.endswith(".py") and f.count("/") <= 2 and "__main__" in self.text(f) \
                    and 'if __name__ == "__main__"' in self.text(f).replace("'", '"'):
                eps.append({"kind": "python __main__", "target": f})
        for f in self.glob("Dockerfile*"):
            m = re.findall(r"^(?:CMD|ENTRYPOINT)\s+(.+)$", self.text(f), re.M)
            if m:
                eps.append({"kind": "docker", "target": f, "command": m[-1].strip()})
        seen, out = set(), []
        for e in eps:
            key = json.dumps(e, sort_keys=True)
            if key not in seen:
                seen.add(key)
                out.append(e)
        return out[:50]

    def scripts(self, deps: list[dict], meta: dict) -> list[dict]:
        out = []
        for d in deps:
            if d["ecosystem"] == "npm":
                pkg = _json(self.text(d["manifest"]))
                for k, v in (pkg.get("scripts") or {}).items():
                    out.append({"source": d["manifest"], "name": k, "command": v})
            if d["ecosystem"] == "composer":
                for k, v in (_json(self.text(d["manifest"])).get("scripts") or {}).items():
                    out.append({"source": d["manifest"], "name": k, "command": v if isinstance(v, str) else " && ".join(v)})
        pp = meta.get("_pyproject", {})
        for k, v in {**pp.get("project", {}).get("scripts", {}),
                     **pp.get("tool", {}).get("poetry", {}).get("scripts", {})}.items():
            out.append({"source": "pyproject.toml", "name": k, "command": v})
        for f in self.named("Makefile", "makefile", "GNUmakefile"):
            t = self.text(f)
            for m in re.finditer(r"^([A-Za-z0-9][\w.-]*)\s*:(?!=)(.*)$", t, re.M):
                body = re.search(rf"^{re.escape(m.group(0))}\n((?:\t.*\n?)+)", t, re.M)
                out.append({"source": f, "name": m.group(1),
                            "command": body.group(1).strip().replace("\t", "") if body else ""})
        for f in self.named("justfile", "Justfile", ".justfile"):
            for m in re.finditer(r"^([A-Za-z0-9][\w-]*)(?:\s+[^:\n]*)?:\s*$", self.text(f), re.M):
                out.append({"source": f, "name": m.group(1), "command": ""})
        return out

    def openapi(self) -> list[dict]:
        out = []
        for f in self.files:
            name = PurePosixPath(f).name.lower()
            if not re.fullmatch(r"(openapi|swagger)[\w.-]*\.(json|ya?ml)", name):
                continue
            t = self.text(f)
            spec = _json(t) if name.endswith(".json") else (_yaml(t) or {})
            paths = spec.get("paths", {}) if isinstance(spec, dict) else {}
            ops = [{"method": m.upper(), "path": p} for p, v in paths.items() if isinstance(v, dict)
                   for m in v if m.lower() in HTTP.split("|")]
            out.append({"file": f, "version": str(spec.get("openapi") or spec.get("swagger") or ""),
                        "title": (spec.get("info") or {}).get("title"), "operations": ops[:300]})
        return out

    def routes(self) -> list[dict]:
        out = []
        code_ext = {".js", ".ts", ".mjs", ".cjs", ".py", ".java", ".kt", ".go", ".rb", ".jsx", ".tsx"}
        for f in self.files:
            p = PurePosixPath(f)
            if is_test(f):
                continue
            # Next.js app router / pages api: route = directory structure
            if p.name.split(".")[0] == "route" and "app" in p.parts and p.suffix in code_ext:
                route = "/" + "/".join(x for x in p.parts[p.parts.index("app") + 1:-1] if not x.startswith("("))
                for m in re.findall(r"export\s+(?:async\s+)?(?:function|const)\s+(GET|POST|PUT|PATCH|DELETE)", self.text(f)):
                    out.append({"method": m, "path": route, "file": f, "framework": "Next.js", "confidence": "high"})
                continue
            if "pages" in p.parts and "api" in p.parts and p.suffix in code_ext:
                i = p.parts.index("api")
                route = "/api/" + "/".join(p.parts[i + 1:-1] + ((p.stem,) if p.stem != "index" else ()))
                out.append({"method": "ANY", "path": route.rstrip("/"), "file": f, "framework": "Next.js", "confidence": "high"})
                continue
            if p.suffix not in code_ext:
                continue
            t = self.text(f)
            if p.name == "urls.py":
                for m in re.finditer(r"\b(?:re_)?path\(\s*r?['\"]([^'\"]*)['\"]", t):
                    out.append({"method": "ANY", "path": "/" + m.group(1), "file": f,
                                "line": t.count("\n", 0, m.start()) + 1, "framework": "Django", "confidence": "medium"})
                continue
            if f.endswith("config/routes.rb"):
                for m in re.finditer(r"^\s*(get|post|put|patch|delete)\s+['\"]([^'\"]+)['\"]", t, re.M):
                    out.append({"method": m.group(1).upper(), "path": m.group(2), "file": f,
                                "line": t.count("\n", 0, m.start()) + 1, "framework": "Rails", "confidence": "medium"})
                for m in re.finditer(r"^\s*resources?\s+:(\w+)", t, re.M):
                    out.append({"method": "REST", "path": "/" + m.group(1), "file": f,
                                "line": t.count("\n", 0, m.start()) + 1, "framework": "Rails", "confidence": "low"})
                continue
            prefix = ""
            if p.suffix == ".py":  # FastAPI APIRouter(prefix="/x")
                pm = re.search(r"APIRouter\([^)]*prefix\s*=\s*['\"]([^'\"]+)['\"]", t)
                prefix = pm.group(1) if pm else ""
            for fw, rx, mg, pg, conf in ROUTE_PATTERNS:
                if fw.startswith(("FastAPI", "Flask")) and p.suffix != ".py":
                    continue
                if fw == "Express/Fastify" and p.suffix not in {".js", ".ts", ".mjs", ".cjs", ".jsx", ".tsx"}:
                    continue
                if fw == "Gin/Echo" and p.suffix != ".go":
                    continue
                if fw == "Spring" and p.suffix not in {".java", ".kt"}:
                    continue
                for m in rx.finditer(t):
                    method = (m.group(mg) or "GET").replace("'", "").replace('"', "").upper()
                    if fw == "Spring" and method == "REQUEST":
                        method = "ANY"
                    out.append({"method": method.replace(" ", ""), "path": prefix + m.group(pg), "file": f,
                                "line": t.count("\n", 0, m.start()) + 1, "framework": fw,
                                "confidence": conf if not prefix else "medium"})
            if len(out) > 500:
                break
        return out[:500]

    def database(self, deps: list[dict], env_names: set[str], infra: dict) -> dict:
        schema = [f for f in self.files if PurePosixPath(f).name in
                  {"schema.prisma", "schema.sql", "schema.rb", "structure.sql", "init.sql"}]
        mig_dirs = Counter()
        for f in self.files:
            for marker in ("migrations/", "alembic/versions/", "db/migrate/", "migrate/"):
                if marker in f and not f.endswith("__init__.py"):
                    mig_dirs[f[: f.index(marker) + len(marker)].rstrip("/")] += 1
                    break
        models = []
        orm_rx = [
            ("Prisma", re.compile(r"^model\s+(\w+)\s*\{", re.M), {".prisma"}),
            ("SQLAlchemy", re.compile(r"^class\s+(\w+)\((?:Base|db\.Model|SQLModel(?:\s*,[^)]*)?)\):", re.M), {".py"}),
            ("Django", re.compile(r"^class\s+(\w+)\((?:models\.)?Model\):", re.M), {".py"}),
            ("TypeORM", re.compile(r"@Entity\([^)]*\)\s*(?:export\s+)?class\s+(\w+)"), {".ts", ".js"}),
            ("Sequelize", re.compile(r"(?:sequelize\.define\(\s*['\"](\w+)['\"]|class\s+(\w+)\s+extends\s+Model\b)"), {".ts", ".js"}),
            ("ActiveRecord", re.compile(r"^class\s+(\w+)\s*<\s*(?:ApplicationRecord|ActiveRecord::Base)", re.M), {".rb"}),
        ]
        for f in self.files:
            suf = PurePosixPath(f).suffix
            if is_test(f) or "migrations" in f:
                continue
            for orm, rx, exts in orm_rx:
                if suf in exts:
                    for m in rx.finditer(self.text(f)):
                        name = next(g for g in m.groups() if g)
                        if orm == "Django" and "django" not in self.text(f):
                            continue
                        models.append({"orm": orm, "name": name, "file": f})
        engines = set()
        blob = " ".join(n for d in deps for n in list(d["runtime"]) + list(d["dev"])).lower()
        blob += " " + " ".join(env_names).lower() + " " + " ".join(infra.get("compose_images", [])).lower()
        for key, eng in (("postgres", "PostgreSQL"), ("psycopg", "PostgreSQL"), ("pg", "PostgreSQL"),
                         ("asyncpg", "PostgreSQL"), ("mysql", "MySQL"), ("mariadb", "MariaDB"),
                         ("sqlite", "SQLite"), ("mongo", "MongoDB"), ("redis", "Redis"),
                         ("dynamodb", "DynamoDB"), ("firestore", "Firestore"), ("cloud_firestore", "Firestore")):
            if re.search(rf"(^|[\s_:/-]){key}", blob):
                engines.add(eng)
        return {"engines": sorted(engines), "schema_files": schema,
                "migrations": [{"dir": k, "count": v} for k, v in mig_dirs.items()],
                "orms": sorted({m["orm"] for m in models}), "models": models[:200]}

    def infra(self) -> dict:
        docker = self.glob("Dockerfile*") + self.glob("*.Dockerfile")
        compose, images = [], []
        for f in self.files:
            if re.fullmatch(r"(docker-)?compose[\w.-]*\.ya?ml", PurePosixPath(f).name):
                d = _yaml(self.text(f)) or {}
                svcs = d.get("services", {}) if isinstance(d, dict) else {}
                compose.append({"file": f, "services": sorted(svcs) if isinstance(svcs, dict) else []})
                images += [str(s.get("image", "")) for s in svcs.values() if isinstance(s, dict)]
        k8s = []
        for f in self.files:
            if f.endswith((".yaml", ".yml")) and re.search(r"^apiVersion:", self.text(f), re.M) \
                    and re.search(r"^kind:\s*(\w+)", self.text(f), re.M):
                k8s.append({"file": f, "kinds": sorted(set(re.findall(r"^kind:\s*(\w+)", self.text(f), re.M)))})
        tf = self.glob("*.tf")
        tf_res = sorted({r for f in tf for r in re.findall(r"^resource\s+\"(\w+)\"", self.text(f), re.M)})
        platforms = [f for f in self.files if PurePosixPath(f).name in
                     {"vercel.json", "netlify.toml", "fly.toml", "Procfile", "app.yaml", "render.yaml",
                      "serverless.yml", "railway.json", "Chart.yaml", "skaffold.yaml"}]
        return {"dockerfiles": docker, "compose": compose, "compose_images": [i for i in images if i],
                "kubernetes": k8s, "terraform": {"files": tf, "resource_types": tf_res},
                "platform_configs": platforms}

    def ci(self) -> list[dict]:
        out = []
        for f in self.files:
            kind = None
            if f.startswith(".github/workflows/") and f.endswith((".yml", ".yaml")):
                kind = "GitHub Actions"
            elif f == ".gitlab-ci.yml":
                kind = "GitLab CI"
            elif f == ".circleci/config.yml":
                kind = "CircleCI"
            elif f in ("Jenkinsfile", "azure-pipelines.yml", "bitbucket-pipelines.yml", ".travis.yml"):
                kind = {"Jenkinsfile": "Jenkins", "azure-pipelines.yml": "Azure Pipelines",
                        "bitbucket-pipelines.yml": "Bitbucket Pipelines", ".travis.yml": "Travis CI"}[f]
            if not kind:
                continue
            t = self.text(f)
            d = _yaml(t) if f.endswith((".yml", ".yaml")) else None
            entry = {"system": kind, "file": f, "secrets": sorted(set(re.findall(r"secrets\.([A-Za-z_][\w]*)", t)))}
            if isinstance(d, dict):
                if kind == "GitHub Actions":
                    trig = d.get("on", d.get(True))  # YAML parses bare `on` as True
                    entry["name"] = d.get("name")
                    entry["triggers"] = sorted(trig) if isinstance(trig, dict) else trig if isinstance(trig, list) else [trig]
                    entry["jobs"] = sorted(d.get("jobs", {}) or {})
                elif kind == "GitLab CI":
                    entry["stages"] = d.get("stages", [])
                    entry["jobs"] = sorted(k for k, v in d.items() if isinstance(v, dict) and "script" in v)
                elif kind == "CircleCI":
                    entry["jobs"] = sorted(d.get("jobs", {}) or {})
            out.append(entry)
        return out

    def tests(self, deps: list[dict]) -> dict:
        files = [f for f in self.files if TEST_FILE.search(f) or
                 (f.startswith(("tests/", "test/", "spec/")) and PurePosixPath(f).suffix in LANG_EXT)]
        names = {n.lower() for d in deps for n in list(d["runtime"]) + list(d["dev"])}
        fw = []
        for key, label in (("jest", "Jest"), ("vitest", "Vitest"), ("mocha", "Mocha"), ("pytest", "pytest"),
                           ("@playwright/test", "Playwright"), ("cypress", "Cypress"), ("rspec", "RSpec"),
                           ("junit", "JUnit"), ("flutter_test", "flutter_test"), ("@testing-library/react", "Testing Library")):
            if any(n == key or n.endswith(":" + key) or n.startswith(key) for n in names):
                fw.append(label)
        if any(f.endswith("_test.go") for f in files):
            fw.append("go test")
        if not fw and any(f.endswith(".py") for f in files):
            fw.append("pytest/unittest")
        cases = sum(len(TEST_CASE.findall(self.text(f))) for f in files[:2000])
        locs = Counter(f.split("/")[0] if "/" in f else "." for f in files)
        cov = [f for f in self.files if PurePosixPath(f).name in
               {".coveragerc", "codecov.yml", ".codecov.yml", ".nycrc", ".nycrc.json"}]
        for f in self.named("pyproject.toml", "setup.cfg"):
            if "[tool.coverage" in self.text(f) or "[coverage:" in self.text(f):
                cov.append(f)
        for f in self.files:
            if re.match(r"(jest|vitest)\.config\.", PurePosixPath(f).name) and "coverage" in self.text(f):
                cov.append(f)
        return {"frameworks": fw, "files": len(files), "cases_approx": cases,
                "locations": dict(locs.most_common(10)), "coverage_config": sorted(set(cov))}

    def env_vars(self) -> list[dict]:
        found: dict[str, dict] = {}
        for f in self.files:
            name = PurePosixPath(f).name
            if re.fullmatch(r"\.env(\.[\w-]+)?", name) and name != ".env":
                if not any(s in name for s in ("example", "sample", "template", "dist", "defaults")):
                    continue  # only documented templates; never real env files
                for m in re.finditer(r"^\s*(?:export\s+)?([A-Z][A-Z0-9_]*)\s*=", self.text(f), re.M):
                    found.setdefault(m.group(1), {"name": m.group(1), "sources": [], "in_example": False})
                    found[m.group(1)]["in_example"] = True
                    found[m.group(1)]["sources"].append(f)
        for f in self.files:
            if PurePosixPath(f).suffix not in LANG_EXT or is_test(f):  # tests fake env vars; not app config
                continue
            for m in ENV_RE.finditer(self.text(f)):
                var = next(g for g in m.groups() if g)
                e = found.setdefault(var, {"name": var, "sources": [], "in_example": False})
                if f not in e["sources"] and len(e["sources"]) < 10:
                    e["sources"].append(f)
        return sorted(found.values(), key=lambda e: e["name"])

    def third_party(self, deps: list[dict], env: list[dict]) -> list[dict]:
        svc: dict[str, set] = {}
        for d in deps:
            for n in d["runtime"]:
                for key, label in THIRD_PARTY.items():
                    if key in n.lower():
                        svc.setdefault(label, set()).add(f"dependency {n} ({d['manifest']})")
        for e in env:
            for prefix, label in ENV_SERVICE.items():
                if e["name"].startswith(prefix):
                    svc.setdefault(label, set()).add(f"env {e['name']}")
        return [{"service": k, "evidence": sorted(v)[:8]} for k, v in sorted(svc.items())]

    def docs(self) -> dict:
        def first(*pats):
            return next((f for f in self.files if "/" not in f and any(
                re.fullmatch(p, f, re.I) for p in pats)), None)
        lic = first(r"LICEN[CS]E(\.\w+)?", r"COPYING")
        lic_type = None
        if lic:
            t = self.text(lic)[:2000]
            for key, name in (("MIT License", "MIT"), ("Apache License", "Apache-2.0"),
                              ("GNU AFFERO", "AGPL-3.0"), ("GNU GENERAL PUBLIC", "GPL"),
                              ("GNU LESSER", "LGPL"), ("Mozilla Public", "MPL-2.0"), ("BSD", "BSD")):
                if key.lower() in t.lower():
                    lic_type = name
                    break
        return {"readme": first(r"README(\.\w+)?"), "changelog": first(r"CHANGELOG(\.\w+)?", r"HISTORY(\.\w+)?"),
                "license": lic, "license_type": lic_type, "contributing": first(r"CONTRIBUTING(\.\w+)?"),
                "security": first(r"SECURITY(\.\w+)?"),
                "codeowners": next((f for f in self.files if f.endswith("CODEOWNERS")), None),
                "docs_dir_files": len([f for f in self.files if f.startswith("docs/") and f.endswith(".md")])}

    def git_info(self) -> dict:
        if git(self.root, "rev-parse", "--is-inside-work-tree") is None:
            return {"is_repo": False}
        info = {"is_repo": True}
        remotes = (git(self.root, "remote", "-v") or "").split()
        if len(remotes) >= 2:
            info["remote_name"] = remotes[0]
            info["remote_url"] = re.sub(r"//[^/@]+@", "//", remotes[1])  # strip credentials
        info["branch"] = (git(self.root, "rev-parse", "--abbrev-ref", "HEAD") or "").strip() or None
        log = git(self.root, "log", "--format=%aI|%ae", "--no-merges")
        if not log:
            return {**info, "commits": 0}
        lines = [l.split("|") for l in log.strip().splitlines()]
        info.update(commits=len(lines), contributors=len({e for _, e in lines}),
                    first_commit=lines[-1][0][:10], last_commit=lines[0][0][:10])
        recent = git(self.root, "log", "--since=90.days", "--format=%h", "--no-merges") or ""
        info["commits_last_90d"] = len(recent.split())
        tags = git(self.root, "tag", "--sort=-creatordate",
                   "--format=%(refname:short)|%(creatordate:short)") or ""
        info["tags"] = [dict(zip(("name", "date"), t.split("|"))) for t in tags.splitlines()[:20]]
        return info

    def ui(self, fw: list[str]) -> tuple[bool, list[str]]:
        ev = [f"framework: {f}" for f in fw if f in FRONTEND | MOBILE]
        ui_ext = Counter(PurePosixPath(f).suffix for f in self.files
                         if PurePosixPath(f).suffix in {".tsx", ".jsx", ".vue", ".svelte", ".html", ".dart", ".swift", ".xml"})
        for ext in (".tsx", ".jsx", ".vue", ".svelte"):
            if ui_ext[ext]:
                ev.append(f"{ui_ext[ext]} {ext} files")
        templates = [f for f in self.files if f.endswith(".html") and ("templates/" in f or f in ("index.html", "public/index.html"))]
        if templates:
            ev.append(f"HTML templates: {', '.join(templates[:3])}")
        if any(f.startswith(("android/app/src/main/res/", "ios/")) or f.endswith(".storyboard")
               or "/res/layout/" in f for f in self.files):
            ev.append("native mobile UI resources")
        return bool(ev), ev


def scan(root: Path, excludes: list[str] | None = None) -> dict:
    s = Scanner(root, excludes or [])
    deps, meta = s.manifests()
    langs = s.languages()
    fw = s.frameworks(deps)
    packages = s.packages(deps)
    env = s.env_vars()
    infra = s.infra()
    has_ui, ui_ev = s.ui(fw)
    git_info = s.git_info()
    code_files = sum(n for lang, n in langs.items() if lang in CODE_LANGS)
    planning = code_files <= 2 and git_info.get("commits", 0) < 10  # empty repo or bare scaffold
    project = {"name": meta.get("name") or root.resolve().name, "version": meta.get("version"),
               "description": meta.get("description"), "license": meta.get("license"),
               "file_count": len(s.files), "code_files": code_files}
    return {
        "project": project,
        "languages": langs,
        "frameworks": fw,
        "project_type": s.project_type(fw, packages, meta, langs),
        "packages": packages,
        "entry_points": s.entry_points(meta),
        "scripts": s.scripts(deps, meta),
        "openapi": s.openapi(),
        "routes": s.routes(),
        "database": s.database(deps, {e["name"] for e in env}, infra),
        "infra": infra,
        "ci": s.ci(),
        "tests": s.tests(deps),
        "env_vars": env,
        "dependencies": deps,
        "third_party": s.third_party(deps, env),
        "docs": s.docs(),
        "git": git_info,
        "has_ui": has_ui,
        "ui_evidence": ui_ev,
        "stage_hint": "planning" if planning else "active",
        "stage_evidence": f"{code_files} code files, {git_info.get('commits', 0)} commits",
    }


def summary(data: dict) -> dict:
    return {"name": data["project"]["name"], "type": data["project_type"]["all"],
            "frameworks": data["frameworks"], "languages": list(data["languages"])[:5],
            "has_ui": data["has_ui"], "stage_hint": data["stage_hint"],
            "routes": len(data["routes"]) + sum(len(o["operations"]) for o in data["openapi"]),
            "models": len(data["database"]["models"]), "env_vars": len(data["env_vars"]),
            "tests": data["tests"]["files"], "ci": [c["system"] for c in data["ci"]],
            "third_party": [t["service"] for t in data["third_party"]]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project", type=Path, help="project root to scan")
    ap.add_argument("--out", type=Path, help="output path (default <project>/docs/.project-docs/scan.json)")
    ap.add_argument("--exclude", action="append", default=[], metavar="GLOB",
                    help="extra paths to skip, e.g. 'scripts/tests/fixtures/*' (repeatable)")
    ap.add_argument("--stdout", action="store_true", help="print the full scan JSON instead of writing a file")
    args = ap.parse_args(argv)
    if not args.project.is_dir():
        print(json.dumps({"error": f"not a directory: {args.project}"}), file=sys.stderr)
        return 2
    data = scan(args.project, args.exclude)
    if args.stdout:
        print(json.dumps(data, indent=2))
        return 0
    out = args.out or args.project / "docs" / ".project-docs" / "scan.json"
    write_json(out, data)
    print(json.dumps({"out": str(out), **summary(data)}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
