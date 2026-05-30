"""
Education service for education-related business logic
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.education import Education
from app.schemas.education import EducationCreate, EducationUpdate
from app.repositories.education_repository import EducationRepository
from app.utils.pagination import PaginatedResult


class EducationService:
    """Service for education-related business logic"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.education_repository = EducationRepository(db)

    async def get_education_by_id(self, education_id: int) -> Optional[Education]:
        return await self.education_repository.get_by_id(education_id)

    async def get_educations(
        self,
        page: int = 1,
        limit: Optional[int] = 10,
        sort_by: str = "sort_order",
        sort_order: str = "ASC",
        keyword: Optional[str] = None,
    ) -> PaginatedResult:
        return await self.education_repository.get_paginated(
            page=page,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
            keyword=keyword,
        )

    async def create_education(self, education_data: EducationCreate) -> Education:
        education_dict = education_data.model_dump()
        education = Education(**education_dict)
        self.db.add(education)
        await self.db.flush()
        await self.db.commit()

        created_id = education.id
        self.db.expire(education)
        return await self.education_repository.get_by_id(created_id)

    async def update_education(self, education_id: int, education_data: EducationUpdate) -> Education:
        education = await self.education_repository.get_by_id(education_id)
        if not education:
            raise NotFoundError("Education not found")

        data = education_data.model_dump(exclude_unset=True)
        for field, value in data.items():
            setattr(education, field, value)

        await self.db.commit()

        updated_id = education.id
        self.db.expire(education)
        return await self.education_repository.get_by_id(updated_id)

    async def delete_education(self, education_id: int) -> bool:
        return await self.education_repository.delete(education_id)
