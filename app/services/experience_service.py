"""
Experience service for experience-related business logic
"""
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.experience import Experience, ExperienceSkill
from app.schemas.experience import ExperienceCreate, ExperienceUpdate
from app.repositories.experience_repository import ExperienceRepository
from app.utils.pagination import PaginatedResult


class ExperienceService:
    """Service for experience-related business logic"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.experience_repository = ExperienceRepository(db)

    async def get_experience_by_id(self, experience_id: int) -> Optional[Experience]:
        return await self.experience_repository.get_by_id_with_relations(experience_id)

    async def get_experiences(
        self,
        page: int = 1,
        limit: Optional[int] = 10,
        sort_by: str = "sort_order",
        sort_order: str = "ASC",
        keyword: Optional[str] = None,
    ) -> PaginatedResult:
        return await self.experience_repository.get_paginated(
            page=page,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
            keyword=keyword,
        )

    async def _sync_skills(self, experience: Experience, skill_ids):
        """Delete and re-insert experience skill relations."""
        if skill_ids is not None:
            for es in list(experience.experience_skills):
                await self.db.delete(es)
            for skill_id in skill_ids:
                self.db.add(ExperienceSkill(
                    id=str(uuid.uuid4()),
                    experience_id=experience.id,
                    skill_id=skill_id,
                ))

    async def create_experience(self, experience_data: ExperienceCreate) -> Experience:
        experience_dict = experience_data.model_dump(exclude={"skill_ids"})
        experience = Experience(**experience_dict)
        self.db.add(experience)
        await self.db.flush()

        for skill_id in (experience_data.skill_ids or []):
            self.db.add(ExperienceSkill(
                id=str(uuid.uuid4()),
                experience_id=experience.id,
                skill_id=skill_id,
            ))

        await self.db.commit()

        created_id = experience.id
        self.db.expire(experience)
        return await self.experience_repository.get_by_id_with_relations(created_id)

    async def update_experience(self, experience_id: int, experience_data: ExperienceUpdate) -> Experience:
        experience = await self.experience_repository.get_by_id_with_relations(experience_id)
        if not experience:
            raise NotFoundError("Experience not found")

        data = experience_data.model_dump(exclude_unset=True, exclude={"skill_ids"})
        for field, value in data.items():
            setattr(experience, field, value)

        skill_ids = experience_data.skill_ids if experience_data.skill_ids is not None else None
        await self._sync_skills(experience, skill_ids)
        await self.db.commit()

        updated_id = experience.id
        self.db.expire(experience)
        return await self.experience_repository.get_by_id_with_relations(updated_id)

    async def delete_experience(self, experience_id: int) -> bool:
        return await self.experience_repository.delete(experience_id)
