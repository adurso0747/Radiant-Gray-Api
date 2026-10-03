"""
database.py
-----------
Async SQLAlchemy engine/session setup. `get_db` is a FastAPI dependency
that hands each request its own session and closes it afterward —
routes depend on it rather than importing `AsyncSessionLocal` directly,
which is also what lets tests swap in an isolated test database (see
tests/conftest.py).
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .config import settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(settings.database_url, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
