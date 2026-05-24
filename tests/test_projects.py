"""
Tests for project endpoints: /api/v1/admin/projects/*

Public endpoints (GET) do not require authentication.
Write endpoints (POST / PUT / DELETE) require authentication.

Not-found behaviour:
- GET by ID returns HTTP 200 with {"success": false, "status": 404} (route-level guard)
- PUT / DELETE raise NotFoundError → exception handler → HTTP 404
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.models.user import User


# ---------------------------------------------------------------------------
# Local payload helpers
# ---------------------------------------------------------------------------

_PROJECT_PAYLOAD = {
    "title": "My Project",
    "slug": "my-project",
    "sub_title": "A sample subtitle",
    "description": "A sample project",
}


# ---------------------------------------------------------------------------
# Local fixture: a persisted project for read / mutate tests
# ---------------------------------------------------------------------------


@pytest.fixture()
async def project(db: AsyncSession) -> Project:
    p = Project(
        title="Existing Project",
        slug="existing-project",
        description="Already in the DB",
    )
    db.add(p)
    await db.commit()
    await db.refresh(p)
    return p


# ---------------------------------------------------------------------------
# List projects
# ---------------------------------------------------------------------------


class TestGetProjects:
    async def test_get_projects_success(
        self, client: AsyncClient, project: Project
    ):
        response = await client.get("/api/v1/admin/projects")

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert isinstance(body["data"], list)
        assert len(body["data"]) >= 1

    async def test_get_projects_returns_pagination_meta(
        self, client: AsyncClient, project: Project
    ):
        response = await client.get("/api/v1/admin/projects", params={"limit": 10})

        assert response.status_code == 200
        assert "pagination" in response.json()

    async def test_get_projects_no_auth_required(self, client: AsyncClient):
        response = await client.get("/api/v1/admin/projects")

        assert response.status_code == 200


# ---------------------------------------------------------------------------
# Get project by ID
# ---------------------------------------------------------------------------


class TestGetProject:
    async def test_get_project_by_id_success(
        self, client: AsyncClient, project: Project
    ):
        response = await client.get(f"/api/v1/admin/projects/{project.id}")

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["id"] == project.id
        assert body["data"]["slug"] == "existing-project"

    async def test_get_project_by_id_not_found(self, client: AsyncClient):
        # Route returns APIResponse.error() (HTTP 200) when not found
        response = await client.get("/api/v1/admin/projects/999999")

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is False
        assert body["status"] == 404


# ---------------------------------------------------------------------------
# Create project
# ---------------------------------------------------------------------------


class TestCreateProject:
    async def test_create_project_success(
        self, client: AsyncClient, test_user: User, auth_headers: dict
    ):
        response = await client.post(
            "/api/v1/admin/projects", json=_PROJECT_PAYLOAD, headers=auth_headers
        )

        assert response.status_code == 201
        body = response.json()
        assert body["success"] is True
        assert body["data"]["slug"] == "my-project"

    async def test_create_project_duplicate_slug(
        self,
        client: AsyncClient,
        project: Project,
        auth_headers: dict,
    ):
        response = await client.post(
            "/api/v1/admin/projects",
            json={
                "title": "Another Project",
                "slug": "existing-project",  # duplicate
            },
            headers=auth_headers,
        )

        assert response.status_code == 400
        assert response.json()["success"] is False

    async def test_create_project_unauthenticated(self, client: AsyncClient):
        response = await client.post("/api/v1/admin/projects", json=_PROJECT_PAYLOAD)

        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Update project
# ---------------------------------------------------------------------------


class TestUpdateProject:
    async def test_update_project_success(
        self,
        client: AsyncClient,
        project: Project,
        auth_headers: dict,
    ):
        response = await client.put(
            f"/api/v1/admin/projects/{project.id}",
            json={"title": "Updated Title", "sub_title": "Updated subtitle"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["title"] == "Updated Title"

    async def test_update_project_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.put(
            "/api/v1/admin/projects/999999",
            json={"title": "Ghost"},
            headers=auth_headers,
        )

        assert response.status_code == 404
        assert response.json()["success"] is False

    async def test_update_project_duplicate_slug(
        self,
        client: AsyncClient,
        project: Project,
        db: AsyncSession,
        auth_headers: dict,
    ):
        other = Project(title="Other", slug="other-project")
        db.add(other)
        await db.commit()
        await db.refresh(other)

        response = await client.put(
            f"/api/v1/admin/projects/{other.id}",
            json={"slug": "existing-project"},  # taken by `project`
            headers=auth_headers,
        )

        assert response.status_code == 400


# ---------------------------------------------------------------------------
# Delete project
# ---------------------------------------------------------------------------


class TestDeleteProject:
    async def test_delete_project_success(
        self,
        client: AsyncClient,
        project: Project,
        auth_headers: dict,
    ):
        response = await client.delete(
            f"/api/v1/admin/projects/{project.id}", headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json()["success"] is True

    async def test_delete_project_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.delete(
            "/api/v1/admin/projects/999999", headers=auth_headers
        )

        assert response.status_code == 404
        assert response.json()["success"] is False

    async def test_delete_project_unauthenticated(
        self, client: AsyncClient, project: Project
    ):
        response = await client.delete(f"/api/v1/admin/projects/{project.id}")

        assert response.status_code == 403
