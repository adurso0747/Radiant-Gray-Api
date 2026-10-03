"""
conftest.py
-----------
Sets test environment variables *before* anything imports app.config
(whose Settings() is built once at import time — see app/config.py),
then swaps the app's real Postgres session for an isolated in-memory
SQLite one via dependency override, so the test suite never touches a
real database or sends a real email.
"""

import os

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("ADMIN_API_KEY", "test-admin-key")
os.environ.setdefault("NOTIFY_EMAIL", "test@example.com")
os.environ.setdefault("RESEND_API_KEY", "")
os.environ.setdefault("ALLOWED_ORIGINS", "http://localhost:5173")
os.environ.setdefault("RATE_LIMIT", "1000/hour")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# A single shared in-memory SQLite connection for the whole test run —
# plain ":memory:" gives each new connection its own empty database,
# which would make tables created in setup invisible to the request
# that runs inside the test. StaticPool pins everything to one
# connection so they share state.
test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)


async def _override_get_db():
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = _override_get_db


@pytest.fixture(autouse=True)
async def _reset_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def client():
    return TestClient(app)
