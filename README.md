# Radiant Gray API

[![CI](https://github.com/adurso0747/Radiant-Gray-Api/actions/workflows/ci.yml/badge.svg)](https://github.com/adurso0747/Radiant-Gray-Api/actions/workflows/ci.yml)

Backend API for [radiantgrayband.com](https://radiantgrayband.com) (site
repo: [Radiant-Gray](https://github.com/adurso0747/Radiant-Gray)). Decap
CMS owns the site's content directly as JSON — this exists for the parts
that need actual server-side logic instead of a flat file: currently,
contact form submissions (validated, rate-limited, stored in Postgres,
with an email notification), replacing Netlify Forms.

Built as a general FastAPI service rather than a single-purpose script —
each feature is its own router + model (see `app/routers/`), so adding
the next one doesn't mean restructuring anything.

## Stack

FastAPI, SQLAlchemy (async) + Alembic, Postgres via
[Neon](https://neon.tech), [Resend](https://resend.com) for email,
slowapi for rate limiting, pytest. Hosted on [Render](https://render.com).

## Running locally

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows; use `source .venv/bin/activate` on macOS/Linux
pip install -r requirements-dev.txt
cp .env.example .env          # fill in DATABASE_URL at minimum
alembic upgrade head
uvicorn app.main:app --reload
```

Comes up at `http://localhost:8000`. `DATABASE_URL` can point at a Neon
branch or any Postgres — nothing in the code is Neon-specific.

```bash
pytest   # runs against an isolated in-memory SQLite DB, no setup needed
```

## Deploying

Postgres via Neon, email via Resend (optional — submissions are still
stored without it), hosted on Render as a free-tier Web Service.
Required env vars: `DATABASE_URL`, `ADMIN_API_KEY`, `NOTIFY_EMAIL`,
`RESEND_API_KEY`, `FROM_EMAIL`, `ALLOWED_ORIGINS` — set in Render's
dashboard, nowhere else.

Build command runs the migration before starting the app each deploy
(Render's free tier doesn't support a separate Pre-Deploy Command):

```
pip install -r requirements.txt && alembic upgrade head
```

Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

The frontend points here via `VITE_CONTACT_API_URL` in
[Radiant-Gray](https://github.com/adurso0747/Radiant-Gray)'s Netlify
build environment.

Render's free tier sleeps when idle; an external pinger against
`/health` (e.g. [UptimeRobot](https://uptimerobot.com)) avoids the
cold-start delay.

## Checking submissions

```bash
curl -H "X-API-Key: <ADMIN_API_KEY>" https://<render-url>/api/submissions
```

## Changing the schema

Edit the model in `app/models.py`, then generate a migration:

```bash
alembic revision --autogenerate -m "describe the change"
alembic upgrade head
```
