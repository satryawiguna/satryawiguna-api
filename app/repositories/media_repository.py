"""
Media repository for media-specific database operations
"""
from typing import Optional

from sqlalchemy import select, desc, asc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.other import Media
from app.repositories.base import BaseRepository
from app.utils.pagination import PaginatedResult, paginate_async


class MediaRepository(BaseRepository[Media]):
    """Repository for Media model"""

    def __init__(self, db: AsyncSession):
        super().__init__(Media, db)

    async def get_by_id(self, id: str) -> Optional[Media]:
        """Override to accept string-based UUID IDs."""
        result = await self.db.execute(
            select(Media).where(Media.id == id)
        )
        return result.scalar_one_or_none()

    async def delete(self, id: str) -> bool:
        """Override to accept string-based UUID IDs."""
        obj = await self.get_by_id(id)
        if obj:
            await self.db.delete(obj)
            await self.db.commit()
            return True
        return False

    async def get_paginated(
        self,
        page: int = 1,
        limit: Optional[int] = 10,
        sort_by: str = "created_at",
        sort_order: str = "DESC",
        keyword: Optional[str] = None,
        **filters,
    ) -> PaginatedResult:
        sort_column = getattr(Media, sort_by, Media.created_at)
        order = desc(sort_column) if sort_order.upper() == "DESC" else asc(sort_column)
        stmt = select(Media).order_by(order)

        if keyword:
            pattern = f"%{keyword}%"
            stmt = stmt.where(Media.file_name.ilike(pattern))

        return await paginate_async(self.db, stmt, page=page, limit=limit)
