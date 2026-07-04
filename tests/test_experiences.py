"""
Tests for experience endpoints:
  - Admin: /api/v1/admin/experiences/* (all routes require auth, including GET)
  - Public: /api/v1/experiences (no auth)

Not-found behaviour (different from skills/projects):
  All not-found cases return HTTP 200 with {"success": false, "status": 404}.
  Routes use APIResponse.error() rather than raising NotFoundError.
"""
import datetime

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.experience import Experience
from app.models.other import Skill
from app.models.user import User


# ---------------------------------------------------------------------------
# Local payload helpers
# ---------------------------------------------------------------------------

_EXPERIENCE_PAYLOAD = {
    "title": "Software Engineer",
    "company": "Acme Corp",
    "employment_type": "FULL_TIME",
    "start_date": "2022-01-01",
    "sort_order": 0,
    "skill_ids": [],
}


# ---------------------------------------------------------------------------
# Local fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
async def skill(db: AsyncSession) -> Skill:
    s = Skill(name="FastAPI", category_id=None, level=85, sort_order=1)
    db.add(s)
    await db.commit()
    await db.refresh(s)
    return s


@pytest.fixture()
async def experience(db: AsyncSession) -> Experience:
    e = Experience(
        title="Backend Developer",
        company="Test Corp",
        employment_type="FULL_TIME",
        start_date=datetime.date(2021, 1, 1),
        sort_order=0,
    )
    db.add(e)
    await db.commit()
    await db.refresh(e)
    return e


# ---------------------------------------------------------------------------
# Admin: List experiences
# ---------------------------------------------------------------------------


class TestGetExperiences:
    async def test_get_experiences_success(
        self, client: AsyncClient, experience: Experience, auth_headers: dict
    ):
        response = await client.get("/api/v1/admin/experiences", headers=auth_headers)

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert isinstance(body["data"], list)
        assert len(body["data"]) >= 1

    async def test_get_experiences_returns_pagination_meta(
        self, client: AsyncClient, experience: Experience, auth_headers: dict
    ):
        response = await client.get(
            "/api/v1/admin/experiences",
            params={"limit": 10},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert "pagination" in response.json()

    async def test_get_experiences_requires_auth(self, client: AsyncClient):
        response = await client.get("/api/v1/admin/experiences")

        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Admin: Get experience by ID
# ---------------------------------------------------------------------------


class TestGetExperience:
    async def test_get_experience_by_id_success(
        self, client: AsyncClient, experience: Experience, auth_headers: dict
    ):
        response = await client.get(
            f"/api/v1/admin/experiences/{experience.id}", headers=auth_headers
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["id"] == experience.id
        assert body["data"]["title"] == "Backend Developer"

    async def test_get_experience_by_id_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.get(
            "/api/v1/admin/experiences/999999", headers=auth_headers
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is False
        assert body["status"] == 404

    async def test_get_experience_requires_auth(self, client: AsyncClient):
        response = await client.get("/api/v1/admin/experiences/1")

        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Admin: Create experience
# ---------------------------------------------------------------------------


class TestCreateExperience:
    async def test_create_experience_success(
        self, client: AsyncClient, test_user: User, auth_headers: dict
    ):
        response = await client.post(
            "/api/v1/admin/experiences",
            json=_EXPERIENCE_PAYLOAD,
            headers=auth_headers,
        )

        assert response.status_code == 201
        body = response.json()
        assert body["success"] is True
        assert body["data"]["title"] == "Software Engineer"
        assert body["data"]["company"] == "Acme Corp"
        assert body["data"]["employment_type"] == "FULL_TIME"
        assert body["data"]["skills"] == []

    async def test_create_experience_with_skills(
        self, client: AsyncClient, skill: Skill, auth_headers: dict
    ):
        payload = {**_EXPERIENCE_PAYLOAD, "skill_ids": [skill.id]}
        response = await client.post(
            "/api/v1/admin/experiences", json=payload, headers=auth_headers
        )

        assert response.status_code == 201
        body = response.json()
        assert body["success"] is True
        assert len(body["data"]["skills"]) == 1
        assert body["data"]["skills"][0]["id"] == skill.id

    async def test_create_experience_unauthenticated(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/admin/experiences", json=_EXPERIENCE_PAYLOAD
        )

        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Admin: Update experience
# ---------------------------------------------------------------------------


class TestUpdateExperience:
    async def test_update_experience_success(
        self,
        client: AsyncClient,
        experience: Experience,
        auth_headers: dict,
    ):
        response = await client.put(
            f"/api/v1/admin/experiences/{experience.id}",
            json={"title": "Senior Backend Developer"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["title"] == "Senior Backend Developer"

    async def test_update_experience_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.put(
            "/api/v1/admin/experiences/999999",
            json={"title": "Ghost"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is False
        assert body["status"] == 404

    async def test_update_experience_unauthenticated(
        self, client: AsyncClient, experience: Experience
    ):
        response = await client.put(
            f"/api/v1/admin/experiences/{experience.id}",
            json={"title": "Unauthorized"},
        )

        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Admin: Delete experience
# ---------------------------------------------------------------------------


class TestDeleteExperience:
    async def test_delete_experience_success(
        self,
        client: AsyncClient,
        experience: Experience,
        auth_headers: dict,
    ):
        response = await client.delete(
            f"/api/v1/admin/experiences/{experience.id}", headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json()["success"] is True

    async def test_delete_experience_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.delete(
            "/api/v1/admin/experiences/999999", headers=auth_headers
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is False
        assert body["status"] == 404

    async def test_delete_experience_unauthenticated(
        self, client: AsyncClient, experience: Experience
    ):
        response = await client.delete(
            f"/api/v1/admin/experiences/{experience.id}"
        )

        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Public: List experiences (no auth required)
# ---------------------------------------------------------------------------


class TestGuestExperiences:
    async def test_guest_get_experiences_success(self, client: AsyncClient):
        response = await client.get("/api/v1/experiences")

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert isinstance(body["data"], list)

    async def test_guest_get_experiences_returns_pagination_meta(
        self, client: AsyncClient
    ):
        response = await client.get("/api/v1/experiences", params={"limit": 10})

        assert response.status_code == 200
        assert "pagination" in response.json()
