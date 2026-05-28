"""
Database connection and session management
"""
from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings


# ---------------------------------------------------------------------------
# Async engine — used by all FastAPI route handlers
# ---------------------------------------------------------------------------
async_engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,  # required: avoids implicit lazy-loads after commit
)

# ---------------------------------------------------------------------------
# Sync engine — kept exclusively for Alembic migrations and CLI seeders.
# Do NOT inject this into FastAPI routes.
# ---------------------------------------------------------------------------
sync_engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

# Shared declarative base (models register themselves here)
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async database dependency for FastAPI routes.

    Yields an AsyncSession that is automatically closed when the
    request finishes, even if an exception is raised.
    """
    async with AsyncSessionLocal() as session:
        yield session
