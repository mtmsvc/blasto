# blasto

Backend for the website of a Latvian driving school, rebuilding its legacy WordPress site ([blasto.lv](https://blasto.lv)) as a Python service. Live at **[blasto.me](https://blasto.me)**.

Current scope: the school's application form - submitted applications are stored in PostgreSQL and managed through an API protected by an admin key.

## Stack
- **API:** FastAPI, Pydantic, pydantic-settings
- **Database:** PostgreSQL 17, SQLAlchemy 2.0 (async, asyncpg), Alembic migrations
- **Quality:** pytest (against a real Postgres), mypy (strict), ruff
- **Delivery:** multi-stage non-root Docker image, GitHub Actions CI/CD, GHCR, Docker Compose, Caddy (reverse proxy, automatic HTTPS), self-managed Linux VM

## API
| Method | Path | Access | Does |
|---|---|---|---|
| `POST` | `/applications` | public | submit an application |
| `GET` | `/applications` | admin key | list applications |
| `GET` | `/applications/{id}` | admin key | one application |
| `PUT` | `/applications/{id}` | admin key | replace an application |
| `DELETE` | `/applications/{id}` | admin key | delete an application |
| `GET` | `/health` | public | liveness check |

Admin endpoints require the header `X-API-Key`. Errors share one JSON shape: `{"error": "<code>", "message": "<text>"}`.

## Project layout
```
src/blasto/
├── main.py              # app, routers, error handler, request logging
├── config.py            # settings from environment variables
├── db.py                # async engine, sessions
├── errors.py            # BlastoError and subclasses
├── models/              # SQLAlchemy tables
├── schemas/             # Pydantic request/response models
├── crud/                # database operations
└── api/                 # routes and the admin-key check
alembic/                 # database migrations
tests/                   # integration tests against Postgres
```

## Run locally
Requirements: [uv](https://docs.astral.sh/uv/), Docker.

```bash
uv sync                                               # install dependencies
sudo docker compose -f pg_compose.yml up -d           # start local Postgres
sudo docker compose -f pg_compose.yml exec db psql -U blasto -d blasto -c 'CREATE DATABASE blasto_test;'   # once, for tests
```

Create `.env` in the project root:
```
LOG_LEVEL=DEBUG
ADMIN_API_KEY=<any local key>
```

```bash
uv run alembic upgrade head                           # create the tables
uv run uvicorn blasto.main:app --reload               # http://127.0.0.1:8000/docs
```

**Checks** (lint, format, types, tests):
```bash
scripts/check.sh
```
Tests run against the separate database `blasto_test` (set in `pyproject.toml` via pytest-env), apply all migrations first, and empty the tables after each test.

## Deploy
Every push to `main` runs the workflow in `.github/workflows/`:
1. **checks** - ruff, mypy, and pytest against a Postgres service container.
2. **deploy** (only if checks pass) - builds the image tagged with the commit SHA, pushes it to GHCR, then over SSH on the server:
   - writes the SHA to `.env` (`IMAGE_TAG=<sha>`),
   - pulls the image,
   - runs `alembic upgrade head` in a one-off container,
   - starts the new version with `docker compose up -d`.

If the migration fails, the deploy stops and the previous version keeps running.

On the server, `~/blasto` holds `compose.yml` (app, Postgres, Caddy), `Caddyfile`, `.env` (image tag, rewritten by every deploy), `app.env` and `db.env` (secrets, server only, `chmod 600`).

## Rollback
Every deployed commit has its own image in GHCR, so rolling back means running an older image.

**1. Pick the version.** On GitHub, open the commits of `main` and choose the last known-good commit showing **2/2** (checks and deploy passed - the image exists). Copy its **full** 40-character SHA; images are tagged with the full SHA. Commits from other branches have no image.

**2. Switch to it on the server:**
```bash
cd ~/blasto
echo IMAGE_TAG=<full SHA> > .env
docker compose up -d          # recreates only the app container; Postgres and Caddy keep running
docker compose ps
```

**3. Bring `main` in line.** The next deploy would bring the newer version back, so revert the bad commit on `main` (`git revert <sha>`, via a PR).

**Limit: rollback does not undo migrations.** It changes the code, not the database. If the newer version ran a migration, the older code runs against the newer schema; undoing a migration is a separate, deliberate step (`alembic downgrade`).

**Tested:** rolled back from `f6428f06db8490a21134ddddaa90fb78bbb56fe7` (index page changed) to `66e15d6752a295f695c9ebec9187f3f5bed07b03`; the previous page was back after `docker compose up -d`.

## Why async matters here
FastAPI runs `async def` endpoints on a single event loop: while one request waits for the database, the loop serves other requests. A **blocking** call inside `async def` - a synchronous database driver, `time.sleep`, a sync HTTP client - stops the whole loop, and every request on the server freezes until it returns.

blasto avoids this by using an async driver end to end: SQLAlchemy's async engine with `asyncpg`, and every database call is awaited (`await session.execute(...)`, `await session.commit()`). While a query runs, the event loop keeps serving other requests. Synchronous code is used only outside the request path, e.g. in the test cleanup.
