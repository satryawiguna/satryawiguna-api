"""
Tests for skill endpoints: /api/v1/admin/skills/*

All endpoints require authentication except GET.

Not-found behaviour:
- GET by ID returns HTTP 200 with {"success": false, "status": 404} (route-level guard)
- PUT / DELETE raise NotFoundError → exception handler → HTTP 404
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.other import Skill
from app.models.user import User


# ---------------------------------------------------------------------------
# Local payload helpers
# ---------------------------------------------------------------------------

_SKILL_PAYLOAD = {
    "name": "Python",
    "category_id": None,
    "level": 90,
    "icon_url": "https://example.com/icons/python.svg",
    "sort_order": 1,
}


# ---------------------------------------------------------------------------
# Local fixture: a persisted skill for read / mutate tests
# ---------------------------------------------------------------------------


@pytest.fixture()
async def skill(db: AsyncSession) -> Skill:
    s = Skill(name="FastAPI", category_id=None, level=85, sort_order=1)
    db.add(s)
    await db.commit()
    await db.refresh(s)
    return s


# ---------------------------------------------------------------------------
# List skills
# ---------------------------------------------------------------------------


class TestGetSkills:
    async def test_get_skills_success(self, client: AsyncClient, skill: Skill):
        response = await client.get("/api/v1/admin/skills")

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert isinstance(body["data"], list)
        assert len(body["data"]) >= 1

    async def test_get_skills_returns_pagination_meta(
        self, client: AsyncClient, skill: Skill
    ):
        response = await client.get("/api/v1/admin/skills", params={"limit": 10})

        assert response.status_code == 200
        assert "pagination" in response.json()

    async def test_get_skills_no_auth_required(self, client: AsyncClient):
        response = await client.get("/api/v1/admin/skills")

        assert response.status_code == 200


# ---------------------------------------------------------------------------
# Get skill by ID
# ---------------------------------------------------------------------------


class TestGetSkill:
    async def test_get_skill_by_id_success(
        self, client: AsyncClient, skill: Skill
    ):
        response = await client.get(f"/api/v1/admin/skills/{skill.id}")

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["id"] == skill.id
        assert body["data"]["name"] == "FastAPI"

    async def test_get_skill_by_id_not_found(self, client: AsyncClient):
        # Route returns APIResponse.error() (HTTP 200) when not found
        response = await client.get("/api/v1/admin/skills/999999")

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is False
        assert body["status"] == 404


# ---------------------------------------------------------------------------
# Create skill
# ---------------------------------------------------------------------------


class TestCreateSkill:
    async def test_create_skill_success(
        self, client: AsyncClient, test_user: User, auth_headers: dict
    ):
        response = await client.post(
            "/api/v1/admin/skills", json=_SKILL_PAYLOAD, headers=auth_headers
        )

        assert response.status_code == 201
        body = response.json()
        assert body["success"] is True
        assert body["data"]["name"] == "Python"
        assert body["data"]["level"] == 90

    async def test_create_skill_unauthenticated(self, client: AsyncClient):
        response = await client.post("/api/v1/admin/skills", json=_SKILL_PAYLOAD)

        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Update skill
# ---------------------------------------------------------------------------


class TestUpdateSkill:
    async def test_update_skill_success(
        self,
        client: AsyncClient,
        skill: Skill,
        auth_headers: dict,
    ):
        response = await client.put(
            f"/api/v1/admin/skills/{skill.id}",
            json={"level": 95},
            headers=auth_headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["level"] == 95

    async def test_update_skill_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.put(
            "/api/v1/admin/skills/999999",
            json={"level": 50},
            headers=auth_headers,
        )

        assert response.status_code == 404
        assert response.json()["success"] is False

    async def test_update_skill_unauthenticated(
        self, client: AsyncClient, skill: Skill
    ):
        response = await client.put(
            f"/api/v1/admin/skills/{skill.id}", json={"level": 50}
        )

        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Delete skill
# ---------------------------------------------------------------------------


class TestDeleteSkill:
    async def test_delete_skill_success(
        self,
        client: AsyncClient,
        skill: Skill,
        auth_headers: dict,
    ):
        response = await client.delete(
            f"/api/v1/admin/skills/{skill.id}", headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json()["success"] is True

    async def test_delete_skill_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.delete(
            "/api/v1/admin/skills/999999", headers=auth_headers
        )

        assert response.status_code == 404
        assert response.json()["success"] is False

    async def test_delete_skill_unauthenticated(
        self, client: AsyncClient, skill: Skill
    ):
        response = await client.delete(f"/api/v1/admin/skills/{skill.id}")

        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Level filter (admin route: /api/v1/admin/skills)
# ---------------------------------------------------------------------------


class TestGetSkillsLevelFilter:
    """Tests for level and level_operator filtering on GET /api/v1/admin/skills"""

    @pytest.fixture()
    async def skills_with_levels(self, db: AsyncSession) -> list[Skill]:
        """Create skills with varying levels for filter testing."""
        skills = [
            Skill(name="Beginner", category_id=None, level=20, sort_order=1),
            Skill(name="Intermediate", category_id=None, level=50, sort_order=2),
            Skill(name="Advanced", category_id=None, level=80, sort_order=3),
            Skill(name="Expert", category_id=None, level=95, sort_order=4),
            Skill(name="NullLevel", category_id=None, level=None, sort_order=5),
            Skill(name="ZeroLevel", category_id=None, level=0, sort_order=6),
        ]
        for s in skills:
            db.add(s)
        await db.commit()
        for s in skills:
            await db.refresh(s)
        return skills

    async def test_level_eq(
        self, client: AsyncClient, skills_with_levels: list[Skill]
    ):
        """level_operator=eq (default) should return exact match."""
        response = await client.get(
            "/api/v1/admin/skills",
            params={"level": 80, "level_operator": "eq"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        names = [s["name"] for s in body["data"]]
        assert "Advanced" in names
        assert "Beginner" not in names
        assert "Expert" not in names

    async def test_level_eq_default_operator(
        self, client: AsyncClient, skills_with_levels: list[Skill]
    ):
        """Omitting level_operator defaults to eq."""
        response = await client.get(
            "/api/v1/admin/skills",
            params={"level": 50},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        names = [s["name"] for s in body["data"]]
        assert "Intermediate" in names
        assert len(body["data"]) == 1

    async def test_level_lt(
        self, client: AsyncClient, skills_with_levels: list[Skill]
    ):
        """level_operator=lt should return skills with level < value."""
        response = await client.get(
            "/api/v1/admin/skills",
            params={"level": 50, "level_operator": "lt"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        names = [s["name"] for s in body["data"]]
        assert "Beginner" in names
        assert "ZeroLevel" in names
        assert "Intermediate" not in names
        assert "Advanced" not in names

    async def test_level_lte(
        self, client: AsyncClient, skills_with_levels: list[Skill]
    ):
        """level_operator=lte should return skills with level <= value."""
        response = await client.get(
            "/api/v1/admin/skills",
            params={"level": 50, "level_operator": "lte"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        names = [s["name"] for s in body["data"]]
        assert "Beginner" in names
        assert "ZeroLevel" in names
        assert "Intermediate" in names
        assert "Advanced" not in names

    async def test_level_gt(
        self, client: AsyncClient, skills_with_levels: list[Skill]
    ):
        """level_operator=gt should return skills with level > value."""
        response = await client.get(
            "/api/v1/admin/skills",
            params={"level": 80, "level_operator": "gt"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        names = [s["name"] for s in body["data"]]
        assert "Expert" in names
        assert "Advanced" not in names
        assert "Intermediate" not in names

    async def test_level_gte(
        self, client: AsyncClient, skills_with_levels: list[Skill]
    ):
        """level_operator=gte should return skills with level >= value."""
        response = await client.get(
            "/api/v1/admin/skills",
            params={"level": 80, "level_operator": "gte"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        names = [s["name"] for s in body["data"]]
        assert "Advanced" in names
        assert "Expert" in names
        assert "Intermediate" not in names
        assert "Beginner" not in names

    async def test_level_filter_no_level_param(
        self, client: AsyncClient, skills_with_levels: list[Skill]
    ):
        """Omitting level entirely should return all skills (no filter)."""
        response = await client.get(
            "/api/v1/admin/skills",
            params={"level_operator": "gte"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        # Should return all 6 skills since level is None (no filter applied)
        assert len(body["data"]) == 6

    async def test_level_filter_invalid_operator(
        self, client: AsyncClient, skills_with_levels: list[Skill]
    ):
        """Invalid level_operator should return 422 error envelope."""
        response = await client.get(
            "/api/v1/admin/skills",
            params={"level": 50, "level_operator": "invalid"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is False
        assert body["status"] == 422
        assert "level_operator" in body["message"]

    async def test_level_zero(
        self, client: AsyncClient, skills_with_levels: list[Skill]
    ):
        """level=0 should filter correctly (ZeroLevel skill)."""
        response = await client.get(
            "/api/v1/admin/skills",
            params={"level": 0, "level_operator": "eq"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        names = [s["name"] for s in body["data"]]
        assert "ZeroLevel" in names
        assert len(body["data"]) == 1

    async def test_level_filter_public_route(
        self, client: AsyncClient, skills_with_levels: list[Skill]
    ):
        """Level filter also works on the public GET /api/v1/skills."""
        response = await client.get(
            "/api/v1/skills",
            params={"level": 80, "level_operator": "gte"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        names = [s["name"] for s in body["data"]]
        assert "Advanced" in names
        assert "Expert" in names
        assert "Beginner" not in names


# ---------------------------------------------------------------------------
# GroupBy (public route: /api/v1/skills)
# ---------------------------------------------------------------------------


class TestGetSkillsGroupBy:
    """Tests for the groupBy parameter on GET /api/v1/skills"""

    @pytest.fixture()
    async def multi_skills(self, db: AsyncSession) -> list[Skill]:
        """Create several skills with varied attributes for grouping tests."""
        skills = [
            Skill(name="Python", category_id=None, level=90, sort_order=1),
            Skill(name="JavaScript", category_id=None, level=85, sort_order=2),
            Skill(name="TypeScript", category_id=None, level=85, sort_order=3),
            Skill(name="Go", category_id=None, level=80, sort_order=4),
            Skill(name="Rust", category_id=None, level=90, sort_order=5),
        ]
        for s in skills:
            db.add(s)
        await db.commit()
        for s in skills:
            await db.refresh(s)
        return skills

    async def test_group_by_level(
        self, client: AsyncClient, multi_skills: list[Skill]
    ):
        """Group by level — data should be an array of arrays grouped by level."""
        response = await client.get(
            "/api/v1/skills", params={"groupBy": "level"}
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert isinstance(body["data"], list)
        assert len(body["data"]) > 0
        # Each element should be a list (group)
        for group in body["data"]:
            assert isinstance(group, list)
            assert len(group) >= 1
        # Verify no pagination when limit=None
        assert "pagination" not in body

    async def test_group_by_level_with_pagination(
        self, client: AsyncClient, multi_skills: list[Skill]
    ):
        """Group by level with pagination — pagination meta present, data grouped."""
        response = await client.get(
            "/api/v1/skills", params={"groupBy": "level", "limit": 10}
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        # Should have pagination meta
        assert "pagination" in body
        pag = body["pagination"]
        assert pag["total"] == 5
        assert pag["page"] == 1
        # Data should be grouped by level
        assert isinstance(body["data"], list)
        for group in body["data"]:
            assert isinstance(group, list)
            # All items in a group should share the same level
            levels = {item["level"] for item in group}
            assert len(levels) == 1

    async def test_group_by_invalid_column(self, client: AsyncClient):
        """Invalid groupBy column returns 422 error."""
        response = await client.get(
            "/api/v1/skills", params={"groupBy": "invalid_column"}
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is False
        assert body["status"] == 422
        assert "invalid_column" in body["message"]

    async def test_group_by_without_pagination_returns_no_pagination_meta(
        self, client: AsyncClient, multi_skills: list[Skill]
    ):
        """groupBy with limit omitted returns grouped data without pagination meta."""
        response = await client.get(
            "/api/v1/skills", params={"groupBy": "sort_order"}
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert "pagination" not in body
        assert isinstance(body["data"], list)
        for group in body["data"]:
            assert isinstance(group, list)

    async def test_group_by_preserves_sort_order_in_groups(
        self, client: AsyncClient, multi_skills: list[Skill]
    ):
        """Items within each group should maintain the default sort_order ordering."""
        response = await client.get(
            "/api/v1/skills", params={"groupBy": "level"}
        )

        assert response.status_code == 200
        body = response.json()
        # Each group should be sorted by sort_order ascending
        for group in body["data"]:
            sort_orders = [item["sort_order"] for item in group]
            assert sort_orders == sorted(sort_orders)
