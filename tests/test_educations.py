"""
Tests for education endpoints:
  - Admin: /api/v1/admin/educations/* (all routes require auth, including GET)
  - Public: /api/v1/educations (no auth)

Not-found behaviour (different from skills/projects):
  All not-found cases return HTTP 200 with {"success": false, "status": 404}.
  Routes use APIResponse.error() rather than raising NotFoundError.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.education import Education
from app.models.user import User


# ---------------------------------------------------------------------------
# Local payload helpers
# ---------------------------------------------------------------------------

_EDUCATION_PAYLOAD = {
    "degree": "Bachelor of Computer Science",
    "institution": "Example University",
    "start_year": 2018,
    "end_year": 2022,
    "sort_order": 0,
}


# ---------------------------------------------------------------------------
# Local fixture
# ---------------------------------------------------------------------------


@pytest.fixture()
async def education(db: AsyncSession) -> Education:
    e = Education(
        degree="Bachelor of Electrical Engineering",
        institution="Udayana University",
        start_year=2001,
        end_year=2006,
        sort_order=0,
    )
    db.add(e)
    await db.commit()
    await db.refresh(e)
    return e


# ---------------------------------------------------------------------------
# Admin: List educations
# ---------------------------------------------------------------------------


class TestGetEducations:
    async def test_get_educations_success(
        self, client: AsyncClient, education: Education, auth_headers: dict
    ):
        response = await client.get("/api/v1/admin/educations", headers=auth_headers)

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert isinstance(body["data"], list)
        assert len(body["data"]) >= 1

    async def test_get_educations_returns_pagination_meta(
        self, client: AsyncClient, education: Education, auth_headers: dict
    ):
        response = await client.get(
            "/api/v1/admin/educations",
            params={"limit": 10},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert "pagination" in response.json()

    async def test_get_educations_requires_auth(self, client: AsyncClient):
        response = await client.get("/api/v1/admin/educations")

        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Admin: Get education by ID
# ---------------------------------------------------------------------------


class TestGetEducation:
    async def test_get_education_by_id_success(
        self, client: AsyncClient, education: Education, auth_headers: dict
    ):
        response = await client.get(
            f"/api/v1/admin/educations/{education.id}", headers=auth_headers
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["id"] == education.id
        assert body["data"]["degree"] == "Bachelor of Electrical Engineering"

    async def test_get_education_by_id_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.get(
            "/api/v1/admin/educations/999999", headers=auth_headers
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is False
        assert body["status"] == 404

    async def test_get_education_requires_auth(self, client: AsyncClient):
        response = await client.get("/api/v1/admin/educations/1")

        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Admin: Create education
# ---------------------------------------------------------------------------


class TestCreateEducation:
    async def test_create_education_success(
        self, client: AsyncClient, test_user: User, auth_headers: dict
    ):
        response = await client.post(
            "/api/v1/admin/educations",
            json=_EDUCATION_PAYLOAD,
            headers=auth_headers,
        )

        assert response.status_code == 201
        body = response.json()
        assert body["success"] is True
        assert body["data"]["degree"] == "Bachelor of Computer Science"
        assert body["data"]["institution"] == "Example University"
        assert body["data"]["start_year"] == 2018
        assert body["data"]["end_year"] == 2022

    async def test_create_education_present_end_year(
        self, client: AsyncClient, auth_headers: dict
    ):
        """end_year is nullable — None means 'present' / currently enrolled."""
        payload = {**_EDUCATION_PAYLOAD, "end_year": None}
        response = await client.post(
            "/api/v1/admin/educations", json=payload, headers=auth_headers
        )

        assert response.status_code == 201
        body = response.json()
        assert body["success"] is True
        assert body["data"]["end_year"] is None

    async def test_create_education_unauthenticated(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/admin/educations", json=_EDUCATION_PAYLOAD
        )

        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Admin: Update education
# ---------------------------------------------------------------------------


class TestUpdateEducation:
    async def test_update_education_success(
        self,
        client: AsyncClient,
        education: Education,
        auth_headers: dict,
    ):
        response = await client.put(
            f"/api/v1/admin/educations/{education.id}",
            json={"degree": "Master of Computer Science"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["degree"] == "Master of Computer Science"

    async def test_update_education_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.put(
            "/api/v1/admin/educations/999999",
            json={"degree": "Ghost Degree"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is False
        assert body["status"] == 404

    async def test_update_education_unauthenticated(
        self, client: AsyncClient, education: Education
    ):
        response = await client.put(
            f"/api/v1/admin/educations/{education.id}",
            json={"degree": "Unauthorized"},
        )

        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Admin: Delete education
# ---------------------------------------------------------------------------


class TestDeleteEducation:
    async def test_delete_education_success(
        self,
        client: AsyncClient,
        education: Education,
        auth_headers: dict,
    ):
        response = await client.delete(
            f"/api/v1/admin/educations/{education.id}", headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json()["success"] is True

    async def test_delete_education_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.delete(
            "/api/v1/admin/educations/999999", headers=auth_headers
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is False
        assert body["status"] == 404

    async def test_delete_education_unauthenticated(
        self, client: AsyncClient, education: Education
    ):
        response = await client.delete(
            f"/api/v1/admin/educations/{education.id}"
        )

        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Public: List educations (no auth required)
# ---------------------------------------------------------------------------


class TestGuestEducations:
    async def test_guest_get_educations_success(self, client: AsyncClient):
        response = await client.get("/api/v1/educations")

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert isinstance(body["data"], list)

    async def test_guest_get_educations_returns_pagination_meta(
        self, client: AsyncClient
    ):
        response = await client.get("/api/v1/educations", params={"limit": 10})

        assert response.status_code == 200
        assert "pagination" in response.json()
