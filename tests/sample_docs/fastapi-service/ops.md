---
title: Ops Pack
subtitle: Ledgerline
version: 1.0.0
date: '2026-10-18'
author: Ledgerline platform team
project: Ledgerline
pack: ops
chapters:
- runbook
confidential: false
---

# Runbook {#ch-runbook}

## Service overview

| | |
|---|---|
| Hosting | Not recorded in the repo ⟨assumption⟩ |
| Components | `api` (FastAPI on uvicorn, port 8000) and `db` (PostgreSQL 16), from `docker-compose.yml` |
| Health endpoint | `GET /health` (`app/main.py`) |
| On-call | Not provided ⟨assumption⟩ |
| Error tracking | Sentry, if `SENTRY_DSN` is set (`app/main.py`) |

## Start, stop, restart

Local or single-host deployment with Docker Compose:

```bash
docker compose up -d            # start api + db
docker compose stop             # stop
docker compose restart api      # restart the API only
```

Without Docker, for development:

```bash
make dev                        # uvicorn app.main:app --reload
```

## Health checks

```bash
curl -fsS http://localhost:8000/health
```

Expected: `{"status":"ok"}`. This only proves the process is up. It doesn't touch the database.

## Routine tasks

| Task | Frequency | Command |
|---|---|---|
| Apply database migrations | each release | `make migrate` |
| Run tests with coverage | each change | `make test` |
| Lint | each change | `make lint` |
| Back up PostgreSQL | not configured | see [Backup and Disaster Recovery](backup-dr.md) |

## Logs

uvicorn writes access and error logs to stdout:

```bash
docker compose logs -f api
docker compose logs -f db
```

## Common problems

### Every `/orders` request returns 500

1. Check: `docker compose exec api printenv API_KEY`
2. Fix: set `API_KEY` in `.env` and run `docker compose up -d api`. `app/auth.py` reads
   `os.environ["API_KEY"]` on each request and raises `KeyError` when it's missing.

### `KeyError: 'DATABASE_URL'`

1. Check: `.env` contains `DATABASE_URL` (see `.env.example`).
2. Fix: add it and restart. `app/db.py` reads it with `os.environ[...]` when the module loads.

### API can't reach the database

1. Check: `docker compose ps db` shows the database as running.
2. Fix: inside Compose, the host must be `db`, not `localhost`:
   `postgresql+psycopg://ledger:<password>@db:5432/ledger`.

### Deploy job fails in GitLab CI

The `deploy` job in `.gitlab-ci.yml` runs `./scripts/deploy.sh`, but that file isn't in the
repository.

> [!WARNING]
> Deploys from `main` fail until `scripts/deploy.sh` is added, or the job is changed to the
> real deploy command.

## Scaling

`docker-compose.yml` defines one `api` container. To handle more load, run several uvicorn
workers (`--workers N`) or more replicas behind a load balancer ⟨untested⟩. The database is
one PostgreSQL instance.

## Escalation

No on-call contact was provided. See [Incident Response](incident-response.md) once it has been written.

# Assumptions and open questions {#ch-assumptions}

Not included: Incident Response, Monitoring and SLOs, Backup and Disaster Recovery, Troubleshooting and FAQ, Third-Party Services Inventory (not selected for this sample).

| # | Chapter | Item | Type | Why unverified | Who can confirm |
|---|---|---|---|---|---|
| A1 | Runbook | Hosting environment | assumption | `hosting: unknown` | DevOps |
| A2 | Runbook | On-call contact | assumption | `oncall_contact: unknown` | engineering manager |
| A3 | Runbook | Scaling commands | assumption | not exercised | DevOps |
| Q1 | Runbook | What should `scripts/deploy.sh` do? | open question | referenced in CI but missing | DevOps |
| Q2 | Runbook | Should `/health` check the database? | open question | currently static | backend lead |
