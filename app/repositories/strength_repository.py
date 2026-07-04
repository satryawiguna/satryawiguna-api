"""
Strength repository for strength-specific database operations
"""
from typing import Optional

from sqlalchemy import select, desc, asc, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.strength import Strength
from app.repositories.base import BaseRepository
from app.utils.pagination import PaginatedResult, paginate_async


class StrengthRepository(BaseRepository[Strength]):
    """Repository for Strength model"""

    def __init__(self, db: AsyncSession):
        super().__init__(Strength, db)

    async def get_paginated(
        self,
        page: int = 1,
        limit: Optional[int] = 10,
        sort_by: str = "sort_order",
        sort_order: str = "ASC",
        keyword: Optional[str] = None,
        **filters,
    ) -> PaginatedResult:
        sort_column = getattr(Strength, sort_by, Strength.sort_order)
        order = asc(sort_column) if sort_order.upper() == "ASC" else desc(sort_column)
        stmt = select(Strength).order_by(order)

        if keyword:
            pattern = f"%{keyword}%"
            stmt = stmt.where(Strength.description.ilike(pattern))

        return await paginate_async(self.db, stmt, page=page, limit=limit)
