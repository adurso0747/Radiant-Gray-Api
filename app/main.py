"""
main.py
-------
FastAPI app entry point — run locally with:
    uvicorn app.main:app --reload
(from inside server/, with the virtualenv active — see server/README.md)

This service exists to own one thing end to end: the Contact page's
submissions. It replaces Netlify Forms (see src/pages/Contact.tsx in
the main site) so there's a real, deployed Python backend behind one
feature, while Decap CMS keeps owning everything else — shows,
releases, members, site text — unchanged. See server/README.md for the
full "why" and deployment steps.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from .config import settings
from .limiter import limiter
from .routers import admin, contact

app = FastAPI(title="Radiant Gray Contact API")

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
    # sleep from inactivity — see server/README.md.
    return {"status": "ok"}
