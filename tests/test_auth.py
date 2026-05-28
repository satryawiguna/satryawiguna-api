"""
Tests for authentication endpoints: /api/v1/auth/*
"""
from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_refresh_token, hash_password
from app.models.user import RefreshToken, User


# ---------------------------------------------------------------------------
# Local fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
async def inactive_user(db: AsyncSession) -> User:
    user = User(
        name="Inactive User",
        email="inactive@example.com",
        password=hash_password("password123"),
        is_active=False,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture()
async def valid_refresh_token(test_user: User, db: AsyncSession) -> str:
    """Persist a valid (non-revoked, non-expired) refresh token for test_user."""
    token_str = create_refresh_token()
    token = RefreshToken(
        token=token_str,
        user_id=test_user.id,
        expires_at=datetime.utcnow() + timedelta(days=7),
        revoked=False,
    )
    db.add(token)
    await db.commit()
    return token_str


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------


class TestLogin:
    async def test_login_success(self, client: AsyncClient, test_user: User):
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "password123"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["message"] == "Login successful"
        assert "accessToken" in body["data"]
        assert "refreshToken" in body["data"]
        assert body["data"]["tokenType"] == "Bearer"
        assert body["data"]["user"]["email"] == "test@example.com"

    async def test_login_wrong_password(self, client: AsyncClient, test_user: User):
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "wrong-password"},
        )

        assert response.status_code == 401

    async def test_login_unknown_email(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "nobody@example.com", "password": "password123"},
        )

        assert response.status_code == 401

    async def test_login_inactive_user(
        self, client: AsyncClient, inactive_user: User
    ):
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "inactive@example.com", "password": "password123"},
        )

        assert response.status_code == 401


# ---------------------------------------------------------------------------
# Refresh token
# ---------------------------------------------------------------------------


class TestRefreshToken:
    async def test_refresh_success(
        self, client: AsyncClient, valid_refresh_token: str
    ):
        response = await client.post(
            "/api/v1/auth/refresh", json={"refreshToken": valid_refresh_token}
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert "accessToken" in body["data"]
        # Token rotation — the new refresh token must differ from the old one
        assert body["data"]["refreshToken"] != valid_refresh_token

    async def test_refresh_invalid_token(self, client: AsyncClient, test_user: User):
        response = await client.post(
            "/api/v1/auth/refresh", json={"refreshToken": "totally-invalid-token"}
        )

        assert response.status_code == 401

    async def test_refresh_revoked_token(
        self, client: AsyncClient, test_user: User, db: AsyncSession
    ):
        token_str = create_refresh_token()
        db.add(
            RefreshToken(
                token=token_str,
                user_id=test_user.id,
                expires_at=datetime.utcnow() + timedelta(days=7),
                revoked=True,
            )
        )
        await db.commit()

        response = await client.post(
            "/api/v1/auth/refresh", json={"refreshToken": token_str}
        )

        assert response.status_code == 401

    async def test_refresh_expired_token(
        self, client: AsyncClient, test_user: User, db: AsyncSession
    ):
        token_str = create_refresh_token()
        db.add(
            RefreshToken(
                token=token_str,
                user_id=test_user.id,
                expires_at=datetime.utcnow() - timedelta(days=1),  # past
                revoked=False,
            )
        )
        await db.commit()

        response = await client.post(
            "/api/v1/auth/refresh", json={"refreshToken": token_str}
        )

        assert response.status_code == 401


# ---------------------------------------------------------------------------
# /me
# ---------------------------------------------------------------------------


class TestMe:
    async def test_get_me_success(
        self, client: AsyncClient, test_user: User, auth_headers: dict
    ):
        response = await client.get("/api/v1/auth/me", headers=auth_headers)

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["email"] == "test@example.com"
        assert body["data"]["id"] == test_user.id

    async def test_get_me_no_token(self, client: AsyncClient):
        # HTTPBearer raises 403 when the Authorization header is absent
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 403

    async def test_get_me_invalid_token(self, client: AsyncClient, test_user: User):
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid.jwt.token"},
        )

        assert response.status_code == 401


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------


class TestLogout:
    async def test_logout_success(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
        valid_refresh_token: str,
    ):
        response = await client.post(
            "/api/v1/auth/logout",
            json={"refreshToken": valid_refresh_token},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["success"] is True

    async def test_logout_unknown_token(
        self, client: AsyncClient, test_user: User, auth_headers: dict
    ):
        response = await client.post(
            "/api/v1/auth/logout",
            json={"refreshToken": "not-a-real-token"},
            headers=auth_headers,
        )

        assert response.status_code == 400

    async def test_logout_unauthenticated(
        self, client: AsyncClient, valid_refresh_token: str
    ):
        response = await client.post(
            "/api/v1/auth/logout", json={"refreshToken": valid_refresh_token}
        )

        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Change password
# ---------------------------------------------------------------------------


class TestChangePassword:
    async def test_change_password_success(
        self, client: AsyncClient, test_user: User, auth_headers: dict
    ):
        response = await client.post(
            "/api/v1/auth/change-password",
            json={
                "currentPassword": "password123",
                "newPassword": "NewPassword456!",
                "newPasswordConfirmation": "NewPassword456!",
            },
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert response.json()["message"] == "Password changed successfully"

    async def test_change_password_wrong_current(
        self, client: AsyncClient, test_user: User, auth_headers: dict
    ):
        response = await client.post(
            "/api/v1/auth/change-password",
            json={
                "currentPassword": "wrong-password",
                "newPassword": "NewPassword456!",
                "newPasswordConfirmation": "NewPassword456!",
            },
            headers=auth_headers,
        )

        assert response.status_code == 400

    async def test_change_password_new_passwords_mismatch(
        self, client: AsyncClient, test_user: User, auth_headers: dict
    ):
        response = await client.post(
            "/api/v1/auth/change-password",
            json={
                "currentPassword": "password123",
                "newPassword": "NewPassword456!",
                "newPasswordConfirmation": "DifferentPassword789!",
            },
            headers=auth_headers,
        )

        assert response.status_code == 400

    async def test_change_password_unauthenticated(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/auth/change-password",
            json={
                "currentPassword": "password123",
                "newPassword": "NewPassword456!",
                "newPasswordConfirmation": "NewPassword456!",
            },
        )

        assert response.status_code == 403
