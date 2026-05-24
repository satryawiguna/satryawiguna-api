"""
Skill service for skill-related business logic
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.other import Skill
from app.schemas.other import SkillCreate, SkillUpdate
from app.repositories.skill_repository import SkillRepository
from app.utils.pagination import PaginatedResult


class SkillService:
    """Service for skill-related business logic"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.skill_repository = SkillRepository(db)

    async def get_skill_by_id(self, skill_id: int) -> Optional[Skill]:
        return await self.skill_repository.get_by_id(skill_id)

    async def get_skills(
        self,
        page: int = 1,
        limit: Optional[int] = 10,
        sort_by: str = "sort_order",
        sort_order: str = "ASC",
        keyword: Optional[str] = None,
        category_id: Optional[int] = None,
    ) -> PaginatedResult:
        return await self.skill_repository.get_paginated(
            page=page,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
            keyword=keyword,
            category_id=category_id,
        )

    async def create_skill(self, skill_data: SkillCreate) -> Skill:
        skill = Skill(**skill_data.model_dump())
        return await self.skill_repository.create(skill)

    async def update_skill(self, skill_id: int, skill_data: SkillUpdate) -> Skill:
        skill = await self.skill_repository.get_by_id(skill_id)
        if not skill:
            raise NotFoundError("Skill not found")

        for field, value in skill_data.model_dump(exclude_unset=True).items():
            setattr(skill, field, value)

        return await self.skill_repository.update(skill)

    async def delete_skill(self, skill_id: int) -> bool:
        skill = await self.skill_repository.get_by_id(skill_id)
        if not skill:
            raise NotFoundError("Skill not found")
        return await self.skill_repository.delete(skill_id)
