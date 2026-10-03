"""
routers/contact.py
-------------------
The one endpoint the frontend actually calls: POST /api/contact. Rate
limited per-IP (see app/limiter.py) since this is the site's only
public write endpoint and the obvious target for spam/abuse.
"""

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..database import get_db
from ..email import send_notification_email
from ..limiter import limiter
from ..models import Submission
from ..schemas import SubmissionCreate

router = APIRouter()


@router.post("/api/contact", status_code=201)
@limiter.limit(settings.rate_limit)
async def submit_contact(
    request: Request,  # noqa: ARG001 — required by slowapi's @limiter.limit
    payload: SubmissionCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    # Honeypot tripped: respond exactly like a real success so the bot
    # doesn't learn it was caught, but don't store or email it.
    if payload.bot_field:
        return {"status": "ok"}

    submission = Submission(name=payload.name, email=payload.email, message=payload.message)
    db.add(submission)
    await db.commit()

    # Queued after the commit, so the submission is safely in Postgres
    # even if the email send fails or Resend is slow.
    background_tasks.add_task(send_notification_email, payload.name, payload.email, payload.message)

    return {"status": "ok"}
