"""
Career Impact repository for career impact-specific database operations
"""
from typing import Optional

from sqlalchemy import select, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.career_impact import CareerImpact
from app.repositories.base import BaseRepository
from app.utils.pagination import PaginatedResult, paginate_async


class CareerImpactRepository(BaseRepository[CareerImpact]):
    """Repository for CareerImpact model"""

    def __init__(self, db: AsyncSession):
        super().__init__(CareerImpact, db)

    async def get_paginated(
        self,
        page: int = 1,
        limit: Optional[int] = 10,
        sort_by: str = "sort_order",
        sort_order: str = "ASC",
        keyword: Optional[str] = None,
        **filters,
    ) -> PaginatedResult:
        sort_column = getattr(CareerImpact, sort_by, CareerImpact.sort_order)
        order = asc(sort_column) if sort_order.upper() == "ASC" else desc(sort_column)
        stmt = select(CareerImpact).order_by(order)

        if keyword:
            pattern = f"%{keyword}%"
            stmt = stmt.where(CareerImpact.title.ilike(pattern))

        return await paginate_async(self.db, stmt, page=page, limit=limit)
