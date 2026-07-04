"""
Tests for career impact endpoints:
  - Admin: /api/v1/admin/career-impacts/* (all routes require auth, including GET)
  - Public: /api/v1/career-impacts (no auth)

Not-found behaviour:
  All not-found cases return HTTP 200 with {"success": false, "status": 404}.
  Routes use APIResponse.error() rather than raising NotFoundError.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.career_impact import CareerImpact
from app.models.user import User


# ---------------------------------------------------------------------------
# Local payload helpers
# ---------------------------------------------------------------------------

_CAREER_IMPACT_PAYLOAD = {
    "title": "Regional Full-Stack Role",
    "description": "Built cross-border event management systems for HK, MY, SG, PH, and ID.",
    "quote": "Scaling platforms for 500k+ daily active users",
    "icon_url": "https://cdn.satryawiguna.me/icons/globe.svg",
    "sort_order": 0,
}

_VALID_PAYLOADS = [
    {"title": "A - Regional Full-Stack Role", "description": "Description A", "quote": "Quote A", "icon_url": "https://cdn.example.com/a.svg", "sort_order": 3},
    {"title": "B - Clean Medic Project", "description": "Description B", "quote": "Quote B", "icon_url": "https://cdn.example.com/b.svg", "sort_order": 1},
    {"title": "C - Next-Gen Integration", "description": "Description C", "quote": "Quote C", "icon_url": "https://cdn.example.com/c.svg", "sort_order": 2},
    {"title": "D - Platform Migration", "description": "Description D", "quote": "Quote D", "icon_url": "https://cdn.example.com/d.svg", "sort_order": 4},
    {"title": "E - Data Pipeline", "description": "Description E", "quote": "Quote E", "icon_url": "https://cdn.example.com/e.svg", "sort_order": 5},
    {"title": "F - DevOps Setup", "description": "Description F", "quote": "Quote F", "icon_url": "https://cdn.example.com/f.svg", "sort_order": 6},
    {"title": "G - API Gateway", "description": "Description G", "quote": "Quote G", "icon_url": "https://cdn.example.com/g.svg", "sort_order": 7},
    {"title": "H - Auth Service", "description": "Description H", "quote": "Quote H", "icon_url": "https://cdn.example.com/h.svg", "sort_order": 8},
    {"title": "I - Notification Hub", "description": "Description I", "quote": "Quote I", "icon_url": "https://cdn.example.com/i.svg", "sort_order": 9},
    {"title": "J - Analytics Dashboard", "description": "Description J", "quote": "Quote J", "icon_url": "https://cdn.example.com/j.svg", "sort_order": 10},
]

_TITLE_TOO_LONG = "x" * 256
_ICON_URL_TOO_LONG = "x" * 501


# ---------------------------------------------------------------------------
# Local fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
async def career_impact(db: AsyncSession) -> CareerImpact:
    ci = CareerImpact(
        title="Regional Full-Stack Role",
        description="Built cross-border event management systems for HK, MY, SG, PH, and ID.",
        quote="Scaling platforms for 500k+ daily active users",
        icon_url="https://cdn.satryawiguna.me/icons/globe.svg",
        sort_order=0,
    )
    db.add(ci)
    await db.commit()
    await db.refresh(ci)
    return ci


@pytest.fixture()
async def multi_career_impacts(db: AsyncSession) -> list[CareerImpact]:
    """Create 10 career impacts with varied titles and sort orders."""
    created = []
    for payload in _VALID_PAYLOADS:
        ci = CareerImpact(
            title=payload["title"],
            description=payload["description"],
            quote=payload["quote"],
            icon_url=payload["icon_url"],
            sort_order=payload["sort_order"],
        )
        db.add(ci)
        created.append(ci)
    await db.commit()
    for ci in created:
        await db.refresh(ci)
    return created


# ---------------------------------------------------------------------------
# Admin: List career impacts — basic
# ---------------------------------------------------------------------------


class TestGetCareerImpacts:
    async def test_get_career_impacts_success(
        self, client: AsyncClient, career_impact: CareerImpact, auth_headers: dict
    ):
        response = await client.get("/api/v1/admin/career-impacts", headers=auth_headers)

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert isinstance(body["data"], list)
        assert len(body["data"]) >= 1

    async def test_get_career_impacts_returns_pagination_meta(
        self, client: AsyncClient, career_impact: CareerImpact, auth_headers: dict
    ):
        response = await client.get(
            "/api/v1/admin/career-impacts",
            params={"limit": 10},
            headers=auth_headers,
        )

        assert response.status_code == 200
        assert "pagination" in response.json()

    async def test_get_career_impacts_requires_auth(self, client: AsyncClient):
        response = await client.get("/api/v1/admin/career-impacts")

        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Admin: List career impacts — empty database
# ---------------------------------------------------------------------------


class TestGetCareerImpactsEmpty:
    async def test_get_career_impacts_empty_db_returns_empty_list(
        self, client: AsyncClient, auth_headers: dict
    ):
        """No career impacts seeded — returns empty list, not an error."""
        response = await client.get("/api/v1/admin/career-impacts", headers=auth_headers)

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"] == []

    async def test_public_get_career_impacts_empty_db_returns_empty_list(
        self, client: AsyncClient
    ):
        """No career impacts seeded — public route returns empty list, not an error."""
        response = await client.get("/api/v1/career-impacts")

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"] == []


# ---------------------------------------------------------------------------
# Admin: List career impacts — sorting
# ---------------------------------------------------------------------------


class TestGetCareerImpactsSorting:
    async def test_get_career_impacts_sorted_by_title_asc(
        self, client: AsyncClient, multi_career_impacts: list[CareerImpact], auth_headers: dict
    ):
        response = await client.get(
            "/api/v1/admin/career-impacts",
            params={"sortBy": "title", "sortOrder": "ASC"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        body = response.json()
        titles = [item["title"] for item in body["data"]]
        assert titles == sorted(titles)

    async def test_get_career_impacts_sorted_by_title_desc(
        self, client: AsyncClient, multi_career_impacts: list[CareerImpact], auth_headers: dict
    ):
        response = await client.get(
            "/api/v1/admin/career-impacts",
            params={"sortBy": "title", "sortOrder": "DESC"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        body = response.json()
        titles = [item["title"] for item in body["data"]]
        assert titles == sorted(titles, reverse=True)

    async def test_get_career_impacts_sorted_by_sort_order_default(
        self, client: AsyncClient, multi_career_impacts: list[CareerImpact], auth_headers: dict
    ):
        """Default sort is sort_order ASC — verify order matches fixture sort_order values."""
        response = await client.get(
            "/api/v1/admin/career-impacts",
            headers=auth_headers,
        )

        assert response.status_code == 200
        body = response.json()
        sort_orders = [item["sort_order"] for item in body["data"]]
        expected = sorted(p["sort_order"] for p in _VALID_PAYLOADS)
        assert sort_orders == expected

    async def test_get_career_impacts_sorted_by_created_at(
        self, client: AsyncClient, multi_career_impacts: list[CareerImpact], auth_headers: dict
    ):
        response = await client.get(
            "/api/v1/admin/career-impacts",
            params={"sortBy": "created_at", "sortOrder": "ASC"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert len(body["data"]) == len(_VALID_PAYLOADS)


# ---------------------------------------------------------------------------
# Admin: List career impacts — keyword filtering
# ---------------------------------------------------------------------------


class TestGetCareerImpactsFiltering:
    async def test_get_career_impacts_keyword_finds_matches(
        self, client: AsyncClient, multi_career_impacts: list[CareerImpact], auth_headers: dict
    ):
        response = await client.get(
            "/api/v1/admin/career-impacts",
            params={"keyword": "Regional"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert len(body["data"]) >= 1
        for item in body["data"]:
            assert "Regional" in item["title"]

    async def test_get_career_impacts_keyword_no_matches_returns_empty_list(
        self, client: AsyncClient, multi_career_impacts: list[CareerImpact], auth_headers: dict
    ):
        response = await client.get(
            "/api/v1/admin/career-impacts",
            params={"keyword": "zzz_nonexistent"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert body["data"] == []

    async def test_get_career_impacts_keyword_case_insensitive(
        self, client: AsyncClient, multi_career_impacts: list[CareerImpact], auth_headers: dict
    ):
        response = await client.get(
            "/api/v1/admin/career-impacts",
            params={"keyword": "regional"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert len(body["data"]) >= 1


# ---------------------------------------------------------------------------
# Admin: List career impacts — pagination edge cases
# ---------------------------------------------------------------------------


class TestGetCareerImpactsPagination:
    async def test_get_career_impacts_page_beyond_range_returns_empty(
        self, client: AsyncClient, multi_career_impacts: list[CareerImpact], auth_headers: dict
    ):
        """Page beyond the last page returns empty data array."""
        response = await client.get(
            "/api/v1/admin/career-impacts",
            params={"page": 999, "limit": 10},
            headers=auth_headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert body["data"] == []
        assert body["pagination"]["page"] == 999
        assert body["pagination"]["total"] == len(_VALID_PAYLOADS)

    async def test_get_career_impacts_custom_page_size(
        self, client: AsyncClient, multi_career_impacts: list[CareerImpact], auth_headers: dict
    ):
        response = await client.get(
            "/api/v1/admin/career-impacts",
            params={"limit": 3},
            headers=auth_headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert len(body["data"]) == 3
        assert body["pagination"]["limit"] == 3
        assert body["pagination"]["totalPages"] == 4  # 10 items, 3 per page

    async def test_get_career_impacts_second_page_returns_remaining(
        self, client: AsyncClient, multi_career_impacts: list[CareerImpact], auth_headers: dict
    ):
        """Page 2 with limit=5 returns items 6–10."""
        response = await client.get(
            "/api/v1/admin/career-impacts",
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
# Admin: Get career impact by ID
# ---------------------------------------------------------------------------


class TestGetCareerImpact:
    async def test_get_career_impact_by_id_success(
        self, client: AsyncClient, career_impact: CareerImpact, auth_headers: dict
    ):
        response = await client.get(
            f"/api/v1/admin/career-impacts/{career_impact.id}", headers=auth_headers
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["id"] == career_impact.id
        assert body["data"]["title"] == "Regional Full-Stack Role"
        assert body["data"]["quote"] == "Scaling platforms for 500k+ daily active users"
        assert body["data"]["icon_url"] == "https://cdn.satryawiguna.me/icons/globe.svg"

    async def test_get_career_impact_by_id_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.get(
            "/api/v1/admin/career-impacts/999999", headers=auth_headers
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is False
        assert body["status"] == 404

    async def test_get_career_impact_by_id_non_integer_returns_422(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.get(
            "/api/v1/admin/career-impacts/abc", headers=auth_headers
        )

        assert response.status_code == 422

    async def test_get_career_impact_requires_auth(self, client: AsyncClient):
        response = await client.get("/api/v1/admin/career-impacts/1")

        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Admin: Create career impact
# ---------------------------------------------------------------------------


class TestCreateCareerImpact:
    async def test_create_career_impact_success(
        self, client: AsyncClient, test_user: User, auth_headers: dict
    ):
        response = await client.post(
            "/api/v1/admin/career-impacts",
            json=_CAREER_IMPACT_PAYLOAD,
            headers=auth_headers,
        )

        assert response.status_code == 201
        body = response.json()
        assert body["success"] is True
        assert body["data"]["title"] == "Regional Full-Stack Role"
        assert body["data"]["description"] == "Built cross-border event management systems for HK, MY, SG, PH, and ID."
        assert body["data"]["quote"] == "Scaling platforms for 500k+ daily active users"
        assert body["data"]["icon_url"] == "https://cdn.satryawiguna.me/icons/globe.svg"
        assert body["data"]["sort_order"] == 0

    async def test_create_career_impact_without_optional_fields(
        self, client: AsyncClient, test_user: User, auth_headers: dict
    ):
        """Only title is required — optional fields can be omitted."""
        response = await client.post(
            "/api/v1/admin/career-impacts",
            json={"title": "Minimal Impact", "sort_order": 0},
            headers=auth_headers,
        )

        assert response.status_code == 201
        body = response.json()
        assert body["data"]["title"] == "Minimal Impact"
        assert body["data"]["description"] is None
        assert body["data"]["quote"] is None
        assert body["data"]["icon_url"] is None

    async def test_create_career_impact_empty_title_returns_422(
        self, client: AsyncClient, test_user: User, auth_headers: dict
    ):
        response = await client.post(
            "/api/v1/admin/career-impacts",
            json={"title": "", "sort_order": 0},
            headers=auth_headers,
        )

        assert response.status_code == 422

    async def test_create_career_impact_title_too_long_returns_422(
        self, client: AsyncClient, test_user: User, auth_headers: dict
    ):
        response = await client.post(
            "/api/v1/admin/career-impacts",
            json={"title": _TITLE_TOO_LONG, "sort_order": 0},
            headers=auth_headers,
        )

        assert response.status_code == 422

    async def test_create_career_impact_icon_url_too_long_returns_422(
        self, client: AsyncClient, test_user: User, auth_headers: dict
    ):
        response = await client.post(
            "/api/v1/admin/career-impacts",
            json={"title": "Valid Title", "icon_url": _ICON_URL_TOO_LONG, "sort_order": 0},
            headers=auth_headers,
        )

        assert response.status_code == 422

    async def test_create_career_impact_unauthenticated(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/admin/career-impacts", json=_CAREER_IMPACT_PAYLOAD
        )

        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Admin: Update career impact
# ---------------------------------------------------------------------------


class TestUpdateCareerImpact:
    async def test_update_career_impact_success(
        self,
        client: AsyncClient,
        career_impact: CareerImpact,
        auth_headers: dict,
    ):
        response = await client.put(
            f"/api/v1/admin/career-impacts/{career_impact.id}",
            json={"title": "Senior Full-Stack Architect"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["title"] == "Senior Full-Stack Architect"

    async def test_update_career_impact_partial_update(
        self,
        client: AsyncClient,
        career_impact: CareerImpact,
        auth_headers: dict,
    ):
        """Update only sort_order — title should remain unchanged."""
        response = await client.put(
            f"/api/v1/admin/career-impacts/{career_impact.id}",
            json={"sort_order": 99},
            headers=auth_headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert body["data"]["sort_order"] == 99
        assert body["data"]["title"] == "Regional Full-Stack Role"

    async def test_update_career_impact_empty_title_returns_422(
        self,
        client: AsyncClient,
        career_impact: CareerImpact,
        auth_headers: dict,
    ):
        response = await client.put(
            f"/api/v1/admin/career-impacts/{career_impact.id}",
            json={"title": ""},
            headers=auth_headers,
        )

        assert response.status_code == 422

    async def test_update_career_impact_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.put(
            "/api/v1/admin/career-impacts/999999",
            json={"title": "Ghost Impact"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is False
        assert body["status"] == 404

    async def test_update_career_impact_unauthenticated(
        self, client: AsyncClient, career_impact: CareerImpact
    ):
        response = await client.put(
            f"/api/v1/admin/career-impacts/{career_impact.id}",
            json={"title": "Hacked"},
        )

        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Admin: Delete career impact
# ---------------------------------------------------------------------------


class TestDeleteCareerImpact:
    async def test_delete_career_impact_success(
        self,
        client: AsyncClient,
        career_impact: CareerImpact,
        auth_headers: dict,
    ):
        response = await client.delete(
            f"/api/v1/admin/career-impacts/{career_impact.id}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True

    async def test_delete_career_impact_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.delete(
            "/api/v1/admin/career-impacts/999999",
            headers=auth_headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is False
        assert body["status"] == 404

    async def test_delete_career_impact_already_deleted_returns_not_found(
        self,
        client: AsyncClient,
        career_impact: CareerImpact,
        auth_headers: dict,
    ):
        """Deleting the same resource twice returns not-found."""
        await client.delete(
            f"/api/v1/admin/career-impacts/{career_impact.id}", headers=auth_headers
        )
        response = await client.delete(
            f"/api/v1/admin/career-impacts/{career_impact.id}", headers=auth_headers
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is False
        assert body["status"] == 404

    async def test_delete_career_impact_unauthenticated(
        self, client: AsyncClient, career_impact: CareerImpact
    ):
        response = await client.delete(f"/api/v1/admin/career-impacts/{career_impact.id}")

        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Public: Get career impacts (no auth required)
# ---------------------------------------------------------------------------


class TestPublicGetCareerImpacts:
    async def test_public_get_career_impacts_no_auth(
        self, client: AsyncClient, career_impact: CareerImpact
    ):
        response = await client.get("/api/v1/career-impacts")

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert isinstance(body["data"], list)
        assert len(body["data"]) >= 1

    async def test_public_get_career_impacts_with_pagination(
        self, client: AsyncClient, career_impact: CareerImpact
    ):
        response = await client.get(
            "/api/v1/career-impacts", params={"limit": 10}
        )

        assert response.status_code == 200
        assert "pagination" in response.json()

    async def test_public_get_career_impacts_default_returns_paginated(
        self, client: AsyncClient, career_impact: CareerImpact
    ):
        """Default limit is 10, so response includes pagination metadata by default."""
        response = await client.get("/api/v1/career-impacts")

        assert response.status_code == 200
        body = response.json()
        # Route defaults limit=10, so pagination is always present
        assert "pagination" in body
