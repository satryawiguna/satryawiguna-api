"""
Category and Tag services
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, DuplicateError
from app.models.blog import Category, Tag
from app.schemas.blog import CategoryCreate, CategoryUpdate, TagCreate, TagUpdate
from app.repositories.blog_repository import CategoryRepository, TagRepository
from app.utils.pagination import PaginatedResult


class CategoryService:
    """Service for category-related business logic"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.category_repository = CategoryRepository(db)

    async def get_category_by_id(self, category_id: int) -> Optional[Category]:
        return await self.category_repository.get_by_id(category_id)

    async def get_categories(
        self,
        page: int = 1,
        limit: Optional[int] = 10,
        sort_by: str = "name",
        sort_order: str = "ASC",
        keyword: Optional[str] = None,
        type: Optional[str] = None,
    ) -> PaginatedResult:
        return await self.category_repository.get_paginated(
            page=page, limit=limit, sort_by=sort_by, sort_order=sort_order, keyword=keyword, type=type
        )

    async def create_category(self, data: CategoryCreate) -> Category:
        existing = await self.category_repository.get_by_slug(data.slug)
        if existing:
            raise DuplicateError("Slug already exists")
        category = Category(**data.model_dump())
        return await self.category_repository.create(category)

    async def update_category(self, category_id: int, data: CategoryUpdate) -> Category:
        category = await self.category_repository.get_by_id(category_id)
        if not category:
            raise NotFoundError("Category not found")
        if data.slug and data.slug != category.slug:
            existing = await self.category_repository.get_by_slug(data.slug)
            if existing:
                raise DuplicateError("Slug already exists")
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(category, field, value)
        return await self.category_repository.update(category)

    async def delete_category(self, category_id: int) -> bool:
        category = await self.category_repository.get_by_id(category_id)
        if not category:
            raise NotFoundError("Category not found")
        return await self.category_repository.delete(category_id)


class TagService:
    """Service for tag-related business logic"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.tag_repository = TagRepository(db)

    async def get_tag_by_id(self, tag_id: int) -> Optional[Tag]:
        return await self.tag_repository.get_by_id(tag_id)

    async def get_tags(
        self,
        page: int = 1,
        limit: Optional[int] = 10,
        sort_by: str = "name",
        sort_order: str = "ASC",
    ) -> PaginatedResult:
        return await self.tag_repository.get_paginated(
            page=page, limit=limit, sort_by=sort_by, sort_order=sort_order
        )

    async def create_tag(self, data: TagCreate) -> Tag:
        existing = await self.tag_repository.get_by_slug(data.slug)
        if existing:
            raise DuplicateError("Slug already exists")
        tag = Tag(**data.model_dump())
        return await self.tag_repository.create(tag)

    async def update_tag(self, tag_id: int, data: TagUpdate) -> Tag:
        tag = await self.tag_repository.get_by_id(tag_id)
        if not tag:
            raise NotFoundError("Tag not found")
        if data.slug and data.slug != tag.slug:
            existing = await self.tag_repository.get_by_slug(data.slug)
            if existing:
                raise DuplicateError("Slug already exists")
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(tag, field, value)
        return await self.tag_repository.update(tag)

    async def delete_tag(self, tag_id: int) -> bool:
        tag = await self.tag_repository.get_by_id(tag_id)
        if not tag:
            raise NotFoundError("Tag not found")
        return await self.tag_repository.delete(tag_id)
