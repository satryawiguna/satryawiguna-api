"""
Experience repository for experience-specific database operations
"""
from typing import Optional

from sqlalchemy import select, desc, asc, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.experience import Experience, ExperienceSkill
from app.repositories.base import BaseRepository
from app.utils.pagination import PaginatedResult, paginate_async


class ExperienceRepository(BaseRepository[Experience]):
    """Repository for Experience model"""

    def __init__(self, db: AsyncSession):
        super().__init__(Experience, db)

    async def get_by_id_with_relations(self, experience_id: int) -> Optional[Experience]:
        result = await self.db.execute(
            select(Experience)
            .options(
                selectinload(Experience.experience_skills).selectinload(ExperienceSkill.skill),
            )
            .where(Experience.id == experience_id)
        )
        return result.scalar_one_or_none()

    async def get_paginated(
        self,
        page: int = 1,
        limit: Optional[int] = 10,
        sort_by: str = "sort_order",
        sort_order: str = "ASC",
        keyword: Optional[str] = None,
        **filters,
    ) -> PaginatedResult:
        sort_column = getattr(Experience, sort_by, Experience.sort_order)
        order = asc(sort_column) if sort_order.upper() == "ASC" else desc(sort_column)
        stmt = (
            select(Experience)
            .options(
                selectinload(Experience.experience_skills).selectinload(ExperienceSkill.skill),
            )
            .order_by(order)
        )

        if keyword:
            pattern = f"%{keyword}%"
            stmt = stmt.where(
                or_(Experience.title.ilike(pattern), Experience.company.ilike(pattern))
            )

        return await paginate_async(self.db, stmt, page=page, limit=limit)
