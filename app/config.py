"""
config.py
---------
Settings loaded from environment variables (or a local `.env` file —
see `.env.example`). One `Settings` instance (`settings`, below) is
built at import time, so every required value must be set before the
app starts — it fails fast on a missing config value instead of
surfacing a confusing error on the first request that needs it.
"""

from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolved relative to this file (server/app/config.py), not the
# process's working directory — so `.env` is found the same way
# whether this runs as `uvicorn app.main:app` from inside server/, or
# as `uvicorn --app-dir server app.main:app` from the repo root (see
# .claude/launch.json).
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding="utf-8", extra="ignore")

    # Postgres connection string (e.g. from Neon). Accepts the plain
    # "postgresql://" form a host's dashboard usually gives you — see
    # normalize_database_url below.
    database_url: str

    # Sent as the X-API-Key header to read submissions via
    # GET /api/submissions. Generate with:
    #   python -c "import secrets; print(secrets.token_urlsafe(32))"
    admin_api_key: str

    # Where new-submission notification emails get sent.
    notify_email: str

    # Resend API key. Leave unset to skip sending notification emails —
    # submissions still get stored in Postgres either way.
    resend_api_key: str | None = None

    # Must be a verified sender/domain in Resend, or their shared
    # onboarding@resend.dev address for testing without domain setup.
    from_email: str = "onboarding@resend.dev"

    # Comma-separated list of origins allowed to call this API.
    allowed_origins: str = "http://localhost:5173"

    # slowapi rate-limit string, e.g. "5/hour" or "10/minute".
    rate_limit: str = "5/hour"

    @field_validator("database_url")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        # SQLAlchemy's async engine needs an explicit driver in the
        # scheme, but Neon (and most hosts) hand out a plain
        # "postgresql://" or "postgres://" connection string — rewrite
        # it rather than asking everyone deploying this to remember to.
        if value.startswith("postgres://"):
            value = "postgresql://" + value[len("postgres://") :]
        if value.startswith("postgresql://"):
            value = "postgresql+asyncpg://" + value[len("postgresql://") :]

        if value.startswith("postgresql+asyncpg://"):
            # asyncpg's connect() takes an `ssl` kwarg, not libpq-style
            # query params — hosts like Neon hand out connection strings
            # with `sslmode=require` (sometimes also `channel_binding=
            # require`), and asyncpg rejects unrecognized ones outright
            # with a TypeError rather than ignoring them. Translate the
            # one that matters and drop the rest.
            parts = urlsplit(value)
            query = dict(parse_qsl(parts.query))
            new_query = {}
            if "sslmode" in query:
                new_query["ssl"] = query["sslmode"]
            value = urlunsplit(parts._replace(query=urlencode(new_query)))

        return value

    @property
    def allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


settings = Settings()
