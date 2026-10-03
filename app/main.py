"""
main.py
-------
FastAPI app entry point — run locally with:
    uvicorn app.main:app --reload
(with the virtualenv active — see README.md)

Backend API for radiantgrayband.com. Decap CMS owns the site's content
(shows, releases, members, text) directly as JSON — this exists for
things that need actual server-side logic instead, starting with
contact form submissions (routers/contact.py). New features live as
their own router + model, same pattern.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from .config import settings
from .limiter import limiter
from .routers import admin, contact

app = FastAPI(title="Radiant Gray API")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-API-Key"],
)

app.include_router(contact.router)
app.include_router(admin.router)


@app.get("/health")
async def health() -> dict[str, str]:
    # Hit by Render's health check, and by an external pinger (e.g.
    # UptimeRobot) to reduce how often the free-tier instance goes to
    # sleep from inactivity.
    return {"status": "ok"}
