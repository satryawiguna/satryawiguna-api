"""
Skill repository for skill-specific database operations
"""
from typing import Optional

from sqlalchemy import select, desc, asc, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.other import Skill
from app.repositories.base import BaseRepository
from app.utils.pagination import PaginatedResult, paginate_async


# Operator mapping for level filtering
# Maps operator names to SQLAlchemy column dunder methods
LEVEL_OPERATORS = {
    "eq": "__eq__",
    "lt": "__lt__",
    "lte": "__le__",
    "gt": "__gt__",
    "gte": "__ge__",
}


class SkillRepository(BaseRepository[Skill]):
    """Repository for Skill model"""

    def __init__(self, db: AsyncSession):
        super().__init__(Skill, db)

    async def get_by_id(self, id: int) -> Optional[Skill]:
        result = await self.db.execute(
            select(Skill)
            .options(selectinload(Skill.category))
            .where(Skill.id == id)
        )
        return result.scalar_one_or_none()

    async def get_paginated(
        self,
        page: int = 1,
        limit: Optional[int] = 10,
        sort_by: str = "sort_order",
        sort_order: str = "ASC",
        keyword: Optional[str] = None,
        category_id: Optional[int] = None,
        level: Optional[int] = None,
        level_operator: str = "eq",
        **filters,
    ) -> PaginatedResult:
        sort_column = getattr(Skill, sort_by, Skill.sort_order)
        order = asc(sort_column) if sort_order.upper() == "ASC" else desc(sort_column)
        stmt = select(Skill).options(selectinload(Skill.category)).order_by(order)

        if keyword:
            pattern = f"%{keyword}%"
            stmt = stmt.where(Skill.name.ilike(pattern))
        if category_id is not None:
            stmt = stmt.where(Skill.category_id == category_id)
        if level is not None:
            op_method = LEVEL_OPERATORS.get(level_operator, "__eq__")
            stmt = stmt.where(getattr(Skill.level, op_method)(level))

        return await paginate_async(self.db, stmt, page=page, limit=limit)

