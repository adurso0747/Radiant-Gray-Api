# Radiant Gray — Contact API

[![CI](https://github.com/adurso0747/Radiant-Gray-Contact-Api/actions/workflows/ci.yml/badge.svg)](https://github.com/adurso0747/Radiant-Gray-Contact-Api/actions/workflows/ci.yml)

A small FastAPI service that owns one thing: submissions from the
Contact page on [radiantgrayband.com](https://radiantgrayband.com) (the
site itself: [Radiant-Gray](https://github.com/adurso0747/Radiant-Gray)).
It replaces Netlify Forms — validates and rate-limits each submission,
stores it in Postgres, and emails a notification — so there's a real,
deployed Python backend behind one feature that actually benefits from
server-side ownership (spam control, a durable record of submissions,
an audit trail).

Everything else on the site (shows, releases, members, photos, site
text) is still owned by Decap CMS, unchanged — this service doesn't
touch any of that. It's a separate repo from the main site specifically
so it reads as its own standalone Python project rather than a
subfolder of a mostly-TypeScript one.

## Stack

FastAPI, SQLAlchemy (async) + Alembic, Postgres via
[Neon](https://neon.tech) (free tier), [Resend](https://resend.com) for
email, slowapi for rate limiting, pytest for tests. Hosted on
[Render](https://render.com)'s free tier.

## Running locally

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows; use `source .venv/bin/activate` on macOS/Linux
pip install -r requirements-dev.txt
cp .env.example .env          # then fill in DATABASE_URL at minimum
alembic upgrade head
uvicorn app.main:app --reload
```

The API comes up at `http://localhost:8000`. For local development you
can point `DATABASE_URL` at a free Neon branch, or any Postgres you
have running — there's nothing Neon-specific about the code itself.

```bash
pytest   # runs against an isolated in-memory SQLite DB, no setup needed
```

## Deploying

1. **Database** — create a free [Neon](https://neon.tech) project, copy
   its connection string.
2. **Email** — create a free [Resend](https://resend.com) account, grab
   an API key. Verifying `radiantgrayband.com` (SPF/DKIM DNS records)
   lets you send from a real address on the domain instead of the
   shared `onboarding@resend.dev`.
3. **Hosting** — on [Render](https://render.com), create a new Web
   Service from this repo. `render.yaml` already describes the
   build/start commands and health check, so Render picks those up
   automatically — you just need to fill in the environment variables
   it lists (`DATABASE_URL`, `ADMIN_API_KEY`, `NOTIFY_EMAIL`,
   `RESEND_API_KEY`, `FROM_EMAIL`, `ALLOWED_ORIGINS`) in Render's
   dashboard.
4. Run the migration against the real database once:
   `DATABASE_URL=<neon connection string> alembic upgrade head`
   (from your machine, with the venv active).
5. On the [main site](https://github.com/adurso0747/Radiant-Gray), set
   `VITE_CONTACT_API_URL` (in Netlify's build environment variables) to
   this service's Render URL, then redeploy the frontend.
6. Optional: point a free pinger (e.g. [UptimeRobot](https://uptimerobot.com))
   at `GET /<render-url>/health` every ~10 minutes — Render's free tier
   spins down an idle instance, which otherwise means a slow first
   response after a quiet period.

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
