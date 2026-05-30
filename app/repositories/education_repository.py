"""
Education repository for education-specific database operations
"""
from typing import Optional

from sqlalchemy import select, desc, asc, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.education import Education
from app.repositories.base import BaseRepository
from app.utils.pagination import PaginatedResult, paginate_async


class EducationRepository(BaseRepository[Education]):
    """Repository for Education model"""

    def __init__(self, db: AsyncSession):
        super().__init__(Education, db)

    async def get_paginated(
        self,
        page: int = 1,
        limit: Optional[int] = 10,
        sort_by: str = "sort_order",
        sort_order: str = "ASC",
        keyword: Optional[str] = None,
        **filters,
    ) -> PaginatedResult:
        sort_column = getattr(Education, sort_by, Education.sort_order)
        order = asc(sort_column) if sort_order.upper() == "ASC" else desc(sort_column)
        stmt = select(Education).order_by(order)

        if keyword:
            pattern = f"%{keyword}%"
            stmt = stmt.where(
                or_(Education.degree.ilike(pattern), Education.institution.ilike(pattern))
            )

        return await paginate_async(self.db, stmt, page=page, limit=limit)
