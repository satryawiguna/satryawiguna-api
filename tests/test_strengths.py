"""
Tests for strength endpoints:
  - Admin: /api/v1/admin/strengths/* (all routes require auth, including GET)
  - Public: /api/v1/strengths (no auth)

Not-found behaviour:
  All not-found cases return HTTP 200 with {"success": false, "status": 404}.
  Routes use APIResponse.error() rather than raising NotFoundError.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.strength import Strength
from app.models.user import User


# ---------------------------------------------------------------------------
# Local payload helpers
# ---------------------------------------------------------------------------

_STRENGTH_PAYLOAD = {
    "description": "System Architecture & Scalability",
    "sort_order": 0,
}

_VALID_PAYLOADS = [
    {"description": "A - Leadership", "sort_order": 3},
    {"description": "B - Communication", "sort_order": 1},
    {"description": "C - Problem Solving", "sort_order": 2},
    {"description": "D - Time Management", "sort_order": 4},
    {"description": "E - Teamwork", "sort_order": 5},
    {"description": "F - Adaptability", "sort_order": 6},
    {"description": "G - Creativity", "sort_order": 7},
    {"description": "H - Critical Thinking", "sort_order": 8},
    {"description": "I - Emotional Intelligence", "sort_order": 9},
    {"description": "J - Conflict Resolution", "sort_order": 10},
]

_DESCRIPTION_TOO_LONG = "x" * 501


# ---------------------------------------------------------------------------
# Local fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
async def strength(db: AsyncSession) -> Strength:
    s = Strength(
        description="Problem Solving & Performance Optimization",
        sort_order=0,
    )
    db.add(s)
    await db.commit()
    await db.refresh(s)
    return s


@pytest.fixture()
async def multi_strengths(db: AsyncSession) -> list[Strength]:
    """Create 10 strengths with varied descriptions and sort orders."""
    created = []
    for payload in _VALID_PAYLOADS:
        s = Strength(description=payload["description"], sort_order=payload["sort_order"])
        db.add(s)
        created.append(s)
    await db.commit()
    for s in created:
        await db.refresh(s)
    return created


# ---------------------------------------------------------------------------
# Admin: List strengths — basic
# ---------------------------------------------------------------------------


class TestGetStrengths:
    async def test_get_strengths_success(
        self, client: AsyncClient, strength: Strength, auth_headers: dict
    ):
        response = await client.get("/api/v1/admin/strengths", headers=auth_headers)

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert isinstance(body["data"], list)
        assert len(body["data"]) >= 1

    async def test_get_strengths_returns_pagination_meta(
        self, client: AsyncClient, strength: Strength, auth_headers: dict
    ):
        response = await client.get(
            "/api/v1/admin/strengths",
            params={"limit": 10},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert "pagination" in response.json()

    async def test_get_strengths_requires_auth(self, client: AsyncClient):
        response = await client.get("/api/v1/admin/strengths")

        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Admin: List strengths — empty database
# ---------------------------------------------------------------------------


class TestGetStrengthsEmpty:
    async def test_get_strengths_empty_db_returns_empty_list(
        self, client: AsyncClient, auth_headers: dict
    ):
        """No strengths seeded — returns empty list, not an error."""
        response = await client.get("/api/v1/admin/strengths", headers=auth_headers)

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"] == []

    async def test_public_get_strengths_empty_db_returns_empty_list(
        self, client: AsyncClient
    ):
        """No strengths seeded — public route returns empty list, not an error."""
        response = await client.get("/api/v1/strengths")

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"] == []


# ---------------------------------------------------------------------------
# Admin: List strengths — sorting
# ---------------------------------------------------------------------------


class TestGetStrengthsSorting:
    async def test_get_strengths_sorted_by_description_asc(
        self, client: AsyncClient, multi_strengths: list[Strength], auth_headers: dict
    ):
        response = await client.get(
            "/api/v1/admin/strengths",
            params={"sortBy": "description", "sortOrder": "ASC"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        body = response.json()
        descriptions = [item["description"] for item in body["data"]]
        # _VALID_PAYLOADS descriptions start with "A - Leadership" .. "J - Conflict Resolution"
        # so ASC should match alphabetical order
        assert descriptions == sorted(descriptions)

    async def test_get_strengths_sorted_by_description_desc(
        self, client: AsyncClient, multi_strengths: list[Strength], auth_headers: dict
    ):
        response = await client.get(
            "/api/v1/admin/strengths",
            params={"sortBy": "description", "sortOrder": "DESC"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        body = response.json()
        descriptions = [item["description"] for item in body["data"]]
        assert descriptions == sorted(descriptions, reverse=True)

    async def test_get_strengths_sorted_by_sort_order_default(
        self, client: AsyncClient, multi_strengths: list[Strength], auth_headers: dict
    ):
        """Default sort is sort_order ASC — verify order matches fixture sort_order values."""
        response = await client.get(
            "/api/v1/admin/strengths",
            headers=auth_headers,
        )

        assert response.status_code == 200
        body = response.json()
        sort_orders = [item["sort_order"] for item in body["data"]]
        expected = sorted(p["sort_order"] for p in _VALID_PAYLOADS)
        assert sort_orders == expected

    async def test_get_strengths_sorted_by_created_at(
        self, client: AsyncClient, multi_strengths: list[Strength], auth_headers: dict
    ):
        response = await client.get(
            "/api/v1/admin/strengths",
            params={"sortBy": "created_at", "sortOrder": "ASC"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        body = response.json()
        # All created in the same fixture, so they should all be present
        assert len(body["data"]) == len(_VALID_PAYLOADS)


# ---------------------------------------------------------------------------
# Admin: List strengths — keyword filtering
# ---------------------------------------------------------------------------


class TestGetStrengthsFiltering:
    async def test_get_strengths_keyword_finds_matches(
        self, client: AsyncClient, multi_strengths: list[Strength], auth_headers: dict
    ):
        response = await client.get(
            "/api/v1/admin/strengths",
            params={"keyword": "Leadership"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert len(body["data"]) >= 1
        for item in body["data"]:
            assert "Leadership" in item["description"]

    async def test_get_strengths_keyword_no_matches_returns_empty_list(
        self, client: AsyncClient, multi_strengths: list[Strength], auth_headers: dict
    ):
        response = await client.get(
            "/api/v1/admin/strengths",
            params={"keyword": "zzz_nonexistent"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert body["data"] == []

    async def test_get_strengths_keyword_case_insensitive(
        self, client: AsyncClient, multi_strengths: list[Strength], auth_headers: dict
    ):
        response = await client.get(
            "/api/v1/admin/strengths",
            params={"keyword": "leadership"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert len(body["data"]) >= 1


# ---------------------------------------------------------------------------
# Admin: List strengths — pagination edge cases
# ---------------------------------------------------------------------------


class TestGetStrengthsPagination:
    async def test_get_strengths_page_beyond_range_returns_empty(
        self, client: AsyncClient, multi_strengths: list[Strength], auth_headers: dict
    ):
        """Page beyond the last page returns empty data array."""
        response = await client.get(
            "/api/v1/admin/strengths",
            params={"page": 999, "limit": 10},
            headers=auth_headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert body["data"] == []
        assert body["pagination"]["page"] == 999
        assert body["pagination"]["total"] == len(_VALID_PAYLOADS)

    async def test_get_strengths_custom_page_size(
        self, client: AsyncClient, multi_strengths: list[Strength], auth_headers: dict
    ):
        response = await client.get(
            "/api/v1/admin/strengths",
            params={"limit": 3},
            headers=auth_headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert len(body["data"]) == 3
        assert body["pagination"]["limit"] == 3
        assert body["pagination"]["totalPages"] == 4  # 10 items, 3 per page

    async def test_get_strengths_second_page_returns_remaining(
        self, client: AsyncClient, multi_strengths: list[Strength], auth_headers: dict
    ):
        """Page 2 with limit=5 returns items 6–10."""
        response = await client.get(
            "/api/v1/admin/strengths",
            params={"page": 2, "limit": 5},
            headers=auth_headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert len(body["data"]) == 5
        assert body["pagination"]["page"] == 2
        assert body["pagination"]["hasPreviousPage"] is True
        assert body["pagination"]["hasNextPage"] is False


# ---------------------------------------------------------------------------
# Admin: Get strength by ID
# ---------------------------------------------------------------------------


class TestGetStrength:
    async def test_get_strength_by_id_success(
        self, client: AsyncClient, strength: Strength, auth_headers: dict
    ):
        response = await client.get(
            f"/api/v1/admin/strengths/{strength.id}", headers=auth_headers
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["id"] == strength.id
        assert body["data"]["description"] == "Problem Solving & Performance Optimization"

    async def test_get_strength_by_id_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.get(
            "/api/v1/admin/strengths/999999", headers=auth_headers
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is False
        assert body["status"] == 404

    async def test_get_strength_by_id_non_integer_returns_422(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.get(
            "/api/v1/admin/strengths/abc", headers=auth_headers
        )

        assert response.status_code == 422

    async def test_get_strength_requires_auth(self, client: AsyncClient):
        response = await client.get("/api/v1/admin/strengths/1")

        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Admin: Create strength
# ---------------------------------------------------------------------------


class TestCreateStrength:
    async def test_create_strength_success(
        self, client: AsyncClient, test_user: User, auth_headers: dict
    ):
        response = await client.post(
            "/api/v1/admin/strengths",
            json=_STRENGTH_PAYLOAD,
            headers=auth_headers,
        )

        assert response.status_code == 201
        body = response.json()
        assert body["success"] is True
        assert body["data"]["description"] == "System Architecture & Scalability"
        assert body["data"]["sort_order"] == 0

    async def test_create_strength_empty_description_returns_422(
        self, client: AsyncClient, test_user: User, auth_headers: dict
    ):
        response = await client.post(
            "/api/v1/admin/strengths",
            json={"description": "", "sort_order": 0},
            headers=auth_headers,
        )

        assert response.status_code == 422

    async def test_create_strength_description_too_long_returns_422(
        self, client: AsyncClient, test_user: User, auth_headers: dict
    ):
        response = await client.post(
            "/api/v1/admin/strengths",
            json={"description": _DESCRIPTION_TOO_LONG, "sort_order": 0},
            headers=auth_headers,
        )

        assert response.status_code == 422

    async def test_create_strength_unauthenticated(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/admin/strengths", json=_STRENGTH_PAYLOAD
        )

        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Admin: Update strength
# ---------------------------------------------------------------------------


class TestUpdateStrength:
    async def test_update_strength_success(
        self,
        client: AsyncClient,
        strength: Strength,
        auth_headers: dict,
    ):
        response = await client.put(
            f"/api/v1/admin/strengths/{strength.id}",
            json={"description": "Team Leadership & Collaboration"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["description"] == "Team Leadership & Collaboration"

    async def test_update_strength_partial_update(
        self,
        client: AsyncClient,
        strength: Strength,
        auth_headers: dict,
    ):
        """Update only sort_order — description should remain unchanged."""
        response = await client.put(
            f"/api/v1/admin/strengths/{strength.id}",
            json={"sort_order": 99},
            headers=auth_headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert body["data"]["sort_order"] == 99
        assert body["data"]["description"] == "Problem Solving & Performance Optimization"

    async def test_update_strength_empty_description_returns_422(
        self,
        client: AsyncClient,
        strength: Strength,
        auth_headers: dict,
    ):
        response = await client.put(
            f"/api/v1/admin/strengths/{strength.id}",
            json={"description": ""},
            headers=auth_headers,
        )

        assert response.status_code == 422

    async def test_update_strength_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.put(
            "/api/v1/admin/strengths/999999",
            json={"description": "Ghost Strength"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is False
        assert body["status"] == 404

    async def test_update_strength_unauthenticated(
        self, client: AsyncClient, strength: Strength
    ):
        response = await client.put(
            f"/api/v1/admin/strengths/{strength.id}",
            json={"description": "Hacked"},
        )

        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Admin: Delete strength
# ---------------------------------------------------------------------------


class TestDeleteStrength:
    async def test_delete_strength_success(
        self,
        client: AsyncClient,
        strength: Strength,
        auth_headers: dict,
    ):
        response = await client.delete(
            f"/api/v1/admin/strengths/{strength.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True

    async def test_delete_strength_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.delete(
            "/api/v1/admin/strengths/999999",
            headers=auth_headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is False
        assert body["status"] == 404

    async def test_delete_strength_already_deleted_returns_not_found(
        self,
        client: AsyncClient,
        strength: Strength,
        auth_headers: dict,
    ):
        """Deleting the same resource twice returns not-found."""
        await client.delete(
            f"/api/v1/admin/strengths/{strength.id}", headers=auth_headers
        )
        response = await client.delete(
            f"/api/v1/admin/strengths/{strength.id}", headers=auth_headers
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is False
        assert body["status"] == 404

    async def test_delete_strength_unauthenticated(
        self, client: AsyncClient, strength: Strength
    ):
        response = await client.delete(f"/api/v1/admin/strengths/{strength.id}")

        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Public: Get strengths (no auth required)
# ---------------------------------------------------------------------------


class TestPublicGetStrengths:
    async def test_public_get_strengths_no_auth(
        self, client: AsyncClient, strength: Strength
    ):
        response = await client.get("/api/v1/strengths")

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert isinstance(body["data"], list)
        assert len(body["data"]) >= 1

    async def test_public_get_strengths_with_pagination(
        self, client: AsyncClient, strength: Strength
    ):
        response = await client.get(
            "/api/v1/strengths", params={"limit": 10}
        )

        assert response.status_code == 200
        assert "pagination" in response.json()

    async def test_public_get_strengths_default_returns_paginated(
        self, client: AsyncClient, strength: Strength
    ):
        """Default limit is 10, so response includes pagination metadata by default."""
        response = await client.get("/api/v1/strengths")

        assert response.status_code == 200
        body = response.json()
        # Route defaults limit=10, so pagination is always present
        assert "pagination" in body
