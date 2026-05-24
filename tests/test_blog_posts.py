"""
Tests for blog post endpoints.

Public endpoints (GET): /api/v1/blog-posts/*
Write endpoints (POST / PUT / DELETE): /api/v1/admin/blog-posts/* (require authentication)

Not-found behaviour:
- GET by ID returns HTTP 200 with {"success": false, "status": 404} (route-level guard)
- PUT / DELETE raise NotFoundError → exception handler → HTTP 404
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.blog import BlogPost
from app.models.user import User


# ---------------------------------------------------------------------------
# Local payload helpers
# ---------------------------------------------------------------------------

_POST_PAYLOAD = {
    "title": "Hello World",
    "slug": "hello-world",
    "excerpt": "A short intro",
    "content": "Full content here",
    "status": "draft",
}


# ---------------------------------------------------------------------------
# Local fixture: a persisted blog post for read / mutate tests
# ---------------------------------------------------------------------------


@pytest.fixture()
async def blog_post(test_user: User, db: AsyncSession) -> BlogPost:
    post = BlogPost(
        title="Existing Post",
        slug="existing-post",
        author_id=test_user.id,
        status="published",
    )
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post


# ---------------------------------------------------------------------------
# List posts
# ---------------------------------------------------------------------------


class TestGetBlogPosts:
    async def test_get_blog_posts_success(
        self, client: AsyncClient, blog_post: BlogPost
    ):
        response = await client.get("/api/v1/blog-posts")

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert isinstance(body["data"], list)
        assert len(body["data"]) >= 1

    async def test_get_blog_posts_returns_pagination_meta(
        self, client: AsyncClient, blog_post: BlogPost
    ):
        response = await client.get("/api/v1/blog-posts", params={"limit": 10})

        assert response.status_code == 200
        assert "pagination" in response.json()

    async def test_get_blog_posts_no_auth_required(self, client: AsyncClient):
        # Public endpoint — should work without an Authorization header
        response = await client.get("/api/v1/blog-posts")

        assert response.status_code == 200


# ---------------------------------------------------------------------------
# Get post by ID
# ---------------------------------------------------------------------------


class TestGetBlogPost:
    async def test_get_blog_post_by_id_success(
        self, client: AsyncClient, blog_post: BlogPost
    ):
        response = await client.get(f"/api/v1/blog-posts/{blog_post.id}")

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["id"] == blog_post.id
        assert body["data"]["slug"] == "existing-post"

    async def test_get_blog_post_by_id_not_found(self, client: AsyncClient):
        # Route returns APIResponse.error() (HTTP 200) when not found
        response = await client.get("/api/v1/blog-posts/999999")

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is False
        assert body["status"] == 404


# ---------------------------------------------------------------------------
# Create post
# ---------------------------------------------------------------------------


class TestCreateBlogPost:
    async def test_create_blog_post_success(
        self,
        client: AsyncClient,
        test_user: User,
        auth_headers: dict,
    ):
        response = await client.post(
            "/api/v1/admin/blog-posts",
            json={**_POST_PAYLOAD, "author_id": test_user.id},
            headers=auth_headers,
        )

        assert response.status_code == 201
        body = response.json()
        assert body["success"] is True
        assert body["data"]["slug"] == "hello-world"

    async def test_create_blog_post_duplicate_slug(
        self,
        client: AsyncClient,
        blog_post: BlogPost,
        test_user: User,
        auth_headers: dict,
    ):
        response = await client.post(
            "/api/v1/admin/blog-posts",
            json={
                "title": "Another Post",
                "slug": "existing-post",  # duplicate
                "status": "draft",
                "author_id": test_user.id,
            },
            headers=auth_headers,
        )

        assert response.status_code == 400
        body = response.json()
        assert body["success"] is False

    async def test_create_blog_post_unauthenticated(
        self, client: AsyncClient, test_user: User
    ):
        response = await client.post(
            "/api/v1/admin/blog-posts",
            json={**_POST_PAYLOAD, "author_id": test_user.id},
        )

        assert response.status_code == 403


# ---------------------------------------------------------------------------
# Update post
# ---------------------------------------------------------------------------


class TestUpdateBlogPost:
    async def test_update_blog_post_success(
        self,
        client: AsyncClient,
        blog_post: BlogPost,
        auth_headers: dict,
    ):
        response = await client.put(
            f"/api/v1/admin/blog-posts/{blog_post.id}",
            json={"title": "Updated Title"},
            headers=auth_headers,
        )

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["title"] == "Updated Title"

    async def test_update_blog_post_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.put(
            "/api/v1/admin/blog-posts/999999",
            json={"title": "Ghost"},
            headers=auth_headers,
        )

        assert response.status_code == 404
        assert response.json()["success"] is False

    async def test_update_blog_post_duplicate_slug(
        self,
        client: AsyncClient,
        blog_post: BlogPost,
        test_user: User,
        db: AsyncSession,
        auth_headers: dict,
    ):
        # Create a second post to steal its slug
        other = BlogPost(title="Other", slug="other-slug", author_id=test_user.id, status="draft")
        db.add(other)
        await db.commit()
        await db.refresh(other)

        response = await client.put(
            f"/api/v1/admin/blog-posts/{other.id}",
            json={"slug": "existing-post"},  # slug already taken by blog_post
            headers=auth_headers,
        )

        assert response.status_code == 400


# ---------------------------------------------------------------------------
# Delete post
# ---------------------------------------------------------------------------


class TestDeleteBlogPost:
    async def test_delete_blog_post_success(
        self,
        client: AsyncClient,
        blog_post: BlogPost,
        auth_headers: dict,
    ):
        response = await client.delete(
            f"/api/v1/admin/blog-posts/{blog_post.id}", headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json()["success"] is True

    async def test_delete_blog_post_not_found(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.delete(
            "/api/v1/admin/blog-posts/999999", headers=auth_headers
        )

        assert response.status_code == 404
        assert response.json()["success"] is False

    async def test_delete_blog_post_unauthenticated(
        self, client: AsyncClient, blog_post: BlogPost
    ):
        response = await client.delete(f"/api/v1/blog-posts/{blog_post.id}")

        assert response.status_code == 403
