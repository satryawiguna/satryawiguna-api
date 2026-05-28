"""
Tests for admin user endpoints: /api/v1/admin/users/*

All endpoints require authentication.

Not-found behaviour:
- GET by ID returns HTTP 200 with {"success": false, "status": 404} (route-level guard)
- PUT / DELETE raise NotFoundError → exception handler → HTTP 404
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.user import User


# ---------------------------------------------------------------------------
# Local fixture: a second user that tests can update / delete
# ---------------------------------------------------------------------------


@pytest.fixture()
async def second_user(db: AsyncSession) -> User:
    user = User(
        name="Second User",
        email="second@example.com",
        password=hash_password("password123"),
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


# ---------------------------------------------------------------------------
# List users
# ---------------------------------------------------------------------------


class TestGetUsers:
    async def test_get_users_success(
        self, client: AsyncClient, test_user: User, auth_headers: dict
    ):
        response = await client.get("/api/v1/admin/users", headers=auth_headers)

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert isinstance(body["data"], list)
        assert len(body["data"]) >= 1

    async def test_get_users_returns_pagination_meta(
        self, client: AsyncClient, test_user: User, auth_headers: dict
    ):
        response = await client.get(
            "/api/v1/admin/users", params={"limit": 10}, headers=auth_headers
        )

        assert response.status_code == 200
        body = response.json()
        assert "pagination" in body
        assert body["pagination"]["total"] >= 1

    async def test_get_users_unauthenticated(self, client: AsyncClient):
        response = await client.get("/api/v1/admin/users")

        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Get user by ID
# ---------------------------------------------------------------------------


class TestGetUser:
    async def test_get_user_by_id_success(
        self, client: AsyncClient, test_user: User, auth_headers: dict
    ):
        response = await client.get(
            f"/api/v1/admin/users/{test_user.id}", headers=auth_headers
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["id"] == test_user.id
        assert body["data"]["email"] == test_user.email

    async def test_get_user_by_id_not_found(
        self, client: AsyncClient, test_user: User, auth_headers: dict
    ):
        # Route returns APIResponse.error() (HTTP 200) when the user doesn't exist
        response = await client.get(
            "/api/v1/admin/users/999999", headers=auth_headers
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is False
        assert body["status"] == 404


# ---------------------------------------------------------------------------
# Create user
# ---------------------------------------------------------------------------


class TestCreateUser:
    async def test_create_user_success(
        self, client: AsyncClient, test_user: User, auth_headers: dict
    ):
        response = await client.post(
            "/api/v1/admin/users",
            json={
                "name": "New User",
                "email": "newuser@example.com",
                "password": "securepassword",
            },
            headers=auth_headers,
        )

        assert response.status_code == 201
        body = response.json()
        assert body["success"] is True
        assert body["data"]["email"] == "newuser@example.com"

    async def test_create_user_duplicate_email(
        self, client: AsyncClient, test_user: User, auth_headers: dict
    ):
        response = await client.post(
            "/api/v1/admin/users",
            json={
                "name": "Duplicate",
                "email": "test@example.com",  # already exists
                "password": "securepassword",
            },
            headers=auth_headers,
        )

        assert response.status_code == 400
        body = response.json()
        assert body["success"] is False

    async def test_create_user_unauthenticated(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/admin/users",
            json={
                "name": "Ghost",
                "email": "ghost@example.com",
                "password": "securepassword",
            },
        )

        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Update user
# ---------------------------------------------------------------------------


class TestUpdateUser:
    async def test_update_user_success(
        self, client: AsyncClient, second_user: User, auth_headers: dict
    ):
        response = await client.put(
            f"/api/v1/admin/users/{second_user.id}",
            json={"name": "Updated Name"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["name"] == "Updated Name"

    async def test_update_user_not_found(
        self, client: AsyncClient, test_user: User, auth_headers: dict
    ):
        response = await client.put(
            "/api/v1/admin/users/999999",
            json={"name": "Ghost"},
            headers=auth_headers,
        )

        assert response.status_code == 404
        body = response.json()
        assert body["success"] is False


# ---------------------------------------------------------------------------
# Delete user
# ---------------------------------------------------------------------------


class TestDeleteUser:
    async def test_delete_user_success(
        self, client: AsyncClient, second_user: User, auth_headers: dict
    ):
        response = await client.delete(
            f"/api/v1/admin/users/{second_user.id}", headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json()["success"] is True

    async def test_delete_user_not_found(
        self, client: AsyncClient, test_user: User, auth_headers: dict
    ):
        response = await client.delete(
            "/api/v1/admin/users/999999", headers=auth_headers
        )

        assert response.status_code == 404
        body = response.json()
        assert body["success"] is False

    async def test_delete_user_unauthenticated(
        self, client: AsyncClient, second_user: User
    ):
        response = await client.delete(f"/api/v1/admin/users/{second_user.id}")

        assert response.status_code == 403
