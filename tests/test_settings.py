"""
Tests for settings endpoints:
  - Admin: GET /api/v1/admin/settings (requires auth)
  - Admin: PUT /api/v1/admin/settings (requires auth)
  - Public: GET /api/v1/settings      (no auth)

Response shape is a flat dict {"KEY": "value"}, not a paginated list.
Not-found is not applicable — GET always returns whatever is in the DB (even empty dict).
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.other import Setting
from app.models.user import User


# ---------------------------------------------------------------------------
# Local fixtures — seed a few known Setting rows
# ---------------------------------------------------------------------------


@pytest.fixture()
async def settings(db: AsyncSession) -> list[Setting]:
    rows = [
        Setting(key="GITHUB_URL", value="https://github.com/satryawiguna"),
        Setting(key="LINKED_IN_URL", value="https://linkedin.com/in/satryawiguna"),
        Setting(key="RESUME_FILE_URL", value=None),
    ]
    for row in rows:
        db.add(row)
    await db.commit()
    return rows


# ---------------------------------------------------------------------------
# Admin: GET /api/v1/admin/settings
# ---------------------------------------------------------------------------


class TestGetSettings:
    async def test_get_settings_success(
        self, client: AsyncClient, settings: list, auth_headers: dict
    ):
        response = await client.get("/api/v1/admin/settings", headers=auth_headers)

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        data = body["data"]
        assert isinstance(data, dict)
        assert data["GITHUB_URL"] == "https://github.com/satryawiguna"
        assert data["LINKED_IN_URL"] == "https://linkedin.com/in/satryawiguna"
        assert data["RESUME_FILE_URL"] is None

    async def test_get_settings_empty_db(
        self, client: AsyncClient, auth_headers: dict
    ):
        """No settings seeded — returns empty dict, not an error."""
        response = await client.get("/api/v1/admin/settings", headers=auth_headers)

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"] == {}

    async def test_get_settings_requires_auth(self, client: AsyncClient):
        response = await client.get("/api/v1/admin/settings")

        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Admin: PUT /api/v1/admin/settings
# ---------------------------------------------------------------------------


class TestUpdateSettings:
    async def test_update_settings_success(
        self, client: AsyncClient, settings: list, auth_headers: dict
    ):
        response = await client.put(
            "/api/v1/admin/settings",
            json={"RESUME_FILE_URL": "https://example.com/resume.pdf"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["RESUME_FILE_URL"] == "https://example.com/resume.pdf"
        # Other keys must still be present and unchanged
        assert body["data"]["GITHUB_URL"] == "https://github.com/satryawiguna"

    async def test_update_settings_creates_new_key(
        self, client: AsyncClient, auth_headers: dict
    ):
        """A key that does not yet exist in the DB is created (upsert)."""
        response = await client.put(
            "/api/v1/admin/settings",
            json={"NEW_KEY": "new-value"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["NEW_KEY"] == "new-value"

    async def test_update_settings_set_null(
        self, client: AsyncClient, settings: list, auth_headers: dict
    ):
        """Setting a value to null is valid."""
        response = await client.put(
            "/api/v1/admin/settings",
            json={"GITHUB_URL": None},
            headers=auth_headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["GITHUB_URL"] is None

    async def test_update_settings_requires_auth(self, client: AsyncClient):
        response = await client.put(
            "/api/v1/admin/settings",
            json={"GITHUB_URL": "https://example.com"},
        )

        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Public: GET /api/v1/settings
# ---------------------------------------------------------------------------


class TestGuestSettings:
    async def test_guest_get_all_settings(
        self, client: AsyncClient, settings: list
    ):
        """No slugs param → all settings returned."""
        response = await client.get("/api/v1/settings")

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert isinstance(body["data"], dict)
        assert "GITHUB_URL" in body["data"]
        assert "LINKED_IN_URL" in body["data"]

    async def test_guest_get_settings_by_slugs(
        self, client: AsyncClient, settings: list
    ):
        response = await client.get(
            "/api/v1/settings",
            params={"slugs": "GITHUB_URL,LINKED_IN_URL"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        data = body["data"]
        assert set(data.keys()) == {"GITHUB_URL", "LINKED_IN_URL"}
        assert data["GITHUB_URL"] == "https://github.com/satryawiguna"

    async def test_guest_get_settings_by_single_slug(
        self, client: AsyncClient, settings: list
    ):
        response = await client.get(
            "/api/v1/settings",
            params={"slugs": "GITHUB_URL"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert list(body["data"].keys()) == ["GITHUB_URL"]

    async def test_guest_get_settings_unknown_slug_returns_empty(
        self, client: AsyncClient, settings: list
    ):
        """Requesting a key that does not exist returns an empty dict, not an error."""
        response = await client.get(
            "/api/v1/settings",
            params={"slugs": "NONEXISTENT_KEY"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"] == {}

    async def test_guest_requires_no_auth(self, client: AsyncClient):
        response = await client.get("/api/v1/settings")

        assert response.status_code == 200
