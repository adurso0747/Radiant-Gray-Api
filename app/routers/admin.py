"""
routers/admin.py
-----------------
Read-only endpoint for the band to check submissions (curl, a browser
hitting it directly, whatever) — gated by require_admin_api_key, never
called from the site's own frontend bundle.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import Submission
from ..schemas import SubmissionOut
from ..security import require_admin_api_key

router = APIRouter(dependencies=[Depends(require_admin_api_key)])


@router.get("/api/submissions", response_model=list[SubmissionOut])
async def list_submissions(
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> list[Submission]:
    result = await db.execute(
        select(Submission)
        # id as a tiebreaker: created_at alone isn't enough to order two
        # submissions landing in the same second — SQLite's
        # CURRENT_TIMESTAMP (used in tests) only has second resolution.
        .order_by(Submission.created_at.desc(), Submission.id.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())
