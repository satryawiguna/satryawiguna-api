"""
Blog service for blog-related business logic
"""
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, DuplicateError
from app.models.blog import BlogPost, BlogPostCategory, BlogPostTag
from app.schemas.blog import BlogPostCreate, BlogPostUpdate
from app.repositories.blog_repository import BlogPostRepository
from app.utils.pagination import PaginatedResult


class BlogPostService:
    """Service for blog post-related business logic"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.blog_post_repository = BlogPostRepository(db)

    async def get_blog_post_by_id(self, post_id: int, published_only: bool = False) -> Optional[BlogPost]:
        post = await self.blog_post_repository.get_by_id_with_relations(post_id)
        if not post:
            return None
        if published_only and post.status != "published":
            return None
        return post

    async def get_blog_post_by_slug(self, slug: str) -> Optional[BlogPost]:
        return await self.blog_post_repository.get_by_slug(slug)

    async def get_blog_posts(
        self,
        page: int = 1,
        limit: Optional[int] = 10,
        sort_by: str = "created_at",
        sort_order: str = "DESC",
        keyword: Optional[str] = None,
        status: Optional[str] = None,
        author_id: Optional[int] = None,
        category_id: Optional[int] = None,
        tag_id: Optional[int] = None,
    ) -> PaginatedResult:
        return await self.blog_post_repository.get_paginated(
            page=page,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
            keyword=keyword,
            status=status,
            author_id=author_id,
            category_id=category_id,
            tag_id=tag_id,
        )

    async def _sync_relations(self, post: BlogPost, category_ids, tag_ids):
        """Delete and re-insert blog post relations."""
        if category_ids is not None:
            for bpc in list(post.blog_post_categories):
                await self.db.delete(bpc)
            for category_id in category_ids:
                self.db.add(BlogPostCategory(id=str(uuid.uuid4()), post_id=post.id, category_id=category_id))

        if tag_ids is not None:
            for bpt in list(post.blog_post_tags):
                await self.db.delete(bpt)
            for tag_id in tag_ids:
                self.db.add(BlogPostTag(id=str(uuid.uuid4()), post_id=post.id, tag_id=tag_id))

    async def create_blog_post(self, post_data: BlogPostCreate) -> BlogPost:
        existing_post = await self.blog_post_repository.get_by_slug(post_data.slug)
        if existing_post:
            raise DuplicateError("Slug already exists")

        post_dict = post_data.model_dump(exclude={"category_ids", "tag_ids"})
        post = BlogPost(**post_dict)
        self.db.add(post)
        await self.db.flush()

        # Directly add relations — no need to iterate over existing ones for a new post.
        # This avoids lazy-loading issues on the newly flushed (persistent) object.
        for category_id in (post_data.category_ids or []):
            self.db.add(BlogPostCategory(id=str(uuid.uuid4()), post_id=post.id, category_id=category_id))
        for tag_id in (post_data.tag_ids or []):
            self.db.add(BlogPostTag(id=str(uuid.uuid4()), post_id=post.id, tag_id=tag_id))

        await self.db.commit()

        # Expire cached state so the re-query populates all relations fresh.
        # Capture ID before expiring — accessing post.id after expire triggers lazy load.
        created_id = post.id
        self.db.expire(post)
        return await self.blog_post_repository.get_by_id_with_relations(created_id)

    async def update_blog_post(self, post_id: int, post_data: BlogPostUpdate) -> BlogPost:
        post = await self.blog_post_repository.get_by_id_with_relations(post_id)
        if not post:
            raise NotFoundError("Blog post not found")

        if post_data.slug and post_data.slug != post.slug:
            existing_post = await self.blog_post_repository.get_by_slug(post_data.slug)
            if existing_post:
                raise DuplicateError("Slug already exists")

        data = post_data.model_dump(exclude_unset=True, exclude={"category_ids", "tag_ids"})
        for field, value in data.items():
            setattr(post, field, value)

        category_ids = post_data.category_ids if post_data.category_ids is not None else None
        tag_ids = post_data.tag_ids if post_data.tag_ids is not None else None

        await self._sync_relations(post, category_ids, tag_ids)
        await self.db.commit()

        # Expire cached state so the re-query populates all relations fresh.
        # Capture ID before expiring — accessing post.id after expire triggers lazy load.
        updated_id = post.id
        self.db.expire(post)
        return await self.blog_post_repository.get_by_id_with_relations(updated_id)

    async def delete_blog_post(self, post_id: int) -> bool:
        post = await self.blog_post_repository.get_by_id(post_id)
        if not post:
            raise NotFoundError("Blog post not found")
        return await self.blog_post_repository.delete(post_id)

