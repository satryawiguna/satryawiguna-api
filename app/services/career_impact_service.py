"""
Career Impact service for career impact-related business logic
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.career_impact import CareerImpact
from app.schemas.career_impact import CareerImpactCreate, CareerImpactUpdate
from app.repositories.career_impact_repository import CareerImpactRepository
from app.utils.pagination import PaginatedResult


class CareerImpactService:
    """Service for career impact-related business logic"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.career_impact_repository = CareerImpactRepository(db)

    async def get_career_impact_by_id(self, career_impact_id: int) -> Optional[CareerImpact]:
        return await self.career_impact_repository.get_by_id(career_impact_id)

    async def get_career_impacts(
        self,
        page: int = 1,
        limit: Optional[int] = 10,
        sort_by: str = "sort_order",
        sort_order: str = "ASC",
        keyword: Optional[str] = None,
    ) -> PaginatedResult:
        return await self.career_impact_repository.get_paginated(
            page=page,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
            keyword=keyword,
        )

    async def create_career_impact(self, career_impact_data: CareerImpactCreate) -> CareerImpact:
        career_impact_dict = career_impact_data.model_dump()
        career_impact = CareerImpact(**career_impact_dict)
        self.db.add(career_impact)
        await self.db.flush()
        await self.db.commit()

        created_id = career_impact.id
        self.db.expire(career_impact)
        return await self.career_impact_repository.get_by_id(created_id)

    async def update_career_impact(self, career_impact_id: int, career_impact_data: CareerImpactUpdate) -> CareerImpact:
        career_impact = await self.career_impact_repository.get_by_id(career_impact_id)
        if not career_impact:
            raise NotFoundError("Career Impact not found")

        data = career_impact_data.model_dump(exclude_unset=True)
        for field, value in data.items():
            setattr(career_impact, field, value)

        await self.db.commit()

        updated_id = career_impact.id
        self.db.expire(career_impact)
        return await self.career_impact_repository.get_by_id(updated_id)

    async def delete_career_impact(self, career_impact_id: int) -> bool:
        return await self.career_impact_repository.delete(career_impact_id)
