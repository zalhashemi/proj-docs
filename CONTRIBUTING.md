# Contributing

Thanks for helping! Read [DEV_GUIDE.md](DEV_GUIDE.md) first: it explains how the skill is
structured and why.

## Setup

```bash
python3 skills/project-docs/scripts/bootstrap.py --install   # venv in ~/.cache/project-docs/venv
~/.cache/project-docs/venv/bin/pip install pytest            # (included in requirements.txt already)
~/.cache/project-docs/venv/bin/python -m pytest tests -q
```

Rendering tests need WeasyPrint (Pango) or Chromium/Chrome, and skip themselves when neither
is present. Mermaid tests need `mmdc` (`npm i -g @mermaid-js/mermaid-cli`).

## Pull request checklist

- [ ] `pytest tests -q` passes
- [ ] `claude plugin validate --strict .` passes (if you touched manifests or `SKILL.md`)
- [ ] New document type: catalog entry + template (see `skills/project-docs/README.md`)
- [ ] Visual changes: render a sample (`samples/`) and look at the pages, not just the tests
- [ ] `SKILL.md` stays under 150 lines; detail goes in `reference/`
- [ ] `CHANGELOG.md` updated

## Ground rules

- Generated documents must never invent facts. See `skills/project-docs/reference/writing-standards.md`.
- Keep scripts stdlib-first, with `--help`, JSON output and nonzero exit codes on failure.
- No network access at runtime.
