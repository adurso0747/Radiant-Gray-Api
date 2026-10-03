"""
email.py
--------
Sends the "new contact submission" notification email via Resend's
HTTP API — no SDK dependency, just a plain POST. Called as a
FastAPI background task (see routers/contact.py) so a slow or failed
email send never delays or breaks the API response; the submission is
already safely in Postgres by the time this runs.
"""

import logging

import httpx

from .config import settings

logger = logging.getLogger(__name__)

RESEND_URL = "https://api.resend.com/emails"


async def send_notification_email(name: str, email: str, message: str) -> None:
    if not settings.resend_api_key:
        logger.warning("RESEND_API_KEY not set — skipping notification email for %s", email)
        return

    payload = {
        "from": settings.from_email,
        "to": [settings.notify_email],
        "reply_to": email,
        "subject": f"New contact form submission from {name}",
        "text": f"From: {name} <{email}>\n\n{message}",
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                RESEND_URL,
                headers={"Authorization": f"Bearer {settings.resend_api_key}"},
                json=payload,
            )
            response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        # Resend's response body has the actual reason (e.g. an
        # unverified domain, or the onboarding@resend.dev sender's
        # restriction to the account's own email) — plain
        # logger.exception() only shows the status code, not that.
        logger.error(
            "Resend rejected the notification email for %s: %s %s — %s",
            email,
            exc.response.status_code,
            exc.response.reason_phrase,
            exc.response.text,
        )
    except httpx.HTTPError:
        logger.exception("Failed to send contact notification email for %s", email)
