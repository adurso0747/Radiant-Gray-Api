"""
schemas.py
----------
Pydantic request/response shapes — distinct from the SQLAlchemy models
in models.py, which describe the database table instead. Keeping them
separate means a column we don't want exposed over the API (none yet,
but e.g. a future internal flag) doesn't need an explicit exclusion.
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class SubmissionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    message: str = Field(min_length=1, max_length=5000)
    # Honeypot — real visitors never see or fill this field in (it's
    # hidden on the frontend); a filled-in value means a bot submitted
    # it. The route accepts the request normally but silently drops it,
    # same behavior the Netlify Forms honeypot had, so bots don't learn
    # they were caught. See routers/contact.py.
    bot_field: str = Field(default="", alias="bot-field")

    model_config = {"populate_by_name": True}


class SubmissionOut(BaseModel):
    id: int
    name: str
    email: str
    message: str
    created_at: datetime

    model_config = {"from_attributes": True}
