"""
Shared pytest fixtures.

JWT_SECRET_KEY is seeded into the environment *before* any app module is
imported, because pydantic-settings validates the key at instantiation time.
"""
import os

os.environ.setdefault(
    "JWT_SECRET_KEY",
    "test-secret-key-minimum-32-chars-long-for-safety",
)

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import BigInteger
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.compiler import compiles

import app.models  # noqa: F401 — side-effect import registers all models with Base.metadata
from app.core.database import Base, get_db


# ---------------------------------------------------------------------------
# SQLite compatibility shim
# ---------------------------------------------------------------------------
# SQLite only supports autoincrement for columns declared as exactly INTEGER.
# Production models use BigInteger (→ BIGINT in MySQL), which SQLite does not
# treat as a rowid-alias.  This compile override renders BigInteger as INTEGER
# for SQLite so that primary-key autoincrement works in the test database.
@compiles(BigInteger, "sqlite")
def _bigint_as_integer(type_, compiler, **kwargs):
    return "INTEGER"
from app.core.security import create_access_token, hash_password
from app.models.user import User
from main import app

_TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


# ---------------------------------------------------------------------------
# Database fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
async def db_engine():
    """Fresh in-memory SQLite engine with all tables created per test."""
    engine = create_async_engine(_TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture()
async def db(db_engine):
    """Async session bound to the per-test engine."""
    session_factory = async_sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        yield session


# ---------------------------------------------------------------------------
# HTTP client fixture
# ---------------------------------------------------------------------------


@pytest.fixture()
async def client(db: AsyncSession):
    """
    AsyncClient wired to the FastAPI app.

    The get_db dependency is overridden so route handlers and the test
    share the exact same session — committed data is immediately visible
    to both sides without needing a second connection.
    """

    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# User / auth fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
async def test_user(db: AsyncSession) -> User:
    """Persist an active user with known credentials."""
    user = User(
        name="Test User",
        email="test@example.com",
        password=hash_password("password123"),
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture()
def auth_headers(test_user: User) -> dict:
    """Authorization headers containing a valid JWT for *test_user*."""
    token = create_access_token(
        {"sub": str(test_user.id), "email": test_user.email, "type": "access"}
    )
    return {"Authorization": f"Bearer {token}"}
