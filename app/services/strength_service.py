"""
Strength service for strength-related business logic
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.strength import Strength
from app.schemas.strength import StrengthCreate, StrengthUpdate
from app.repositories.strength_repository import StrengthRepository
from app.utils.pagination import PaginatedResult


class StrengthService:
    """Service for strength-related business logic"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.strength_repository = StrengthRepository(db)

    async def get_strength_by_id(self, strength_id: int) -> Optional[Strength]:
        return await self.strength_repository.get_by_id(strength_id)

    async def get_strengths(
        self,
        page: int = 1,
        limit: Optional[int] = 10,
        sort_by: str = "sort_order",
        sort_order: str = "ASC",
        keyword: Optional[str] = None,
    ) -> PaginatedResult:
        return await self.strength_repository.get_paginated(
            page=page,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
            keyword=keyword,
        )

    async def create_strength(self, strength_data: StrengthCreate) -> Strength:
        strength_dict = strength_data.model_dump()
        strength = Strength(**strength_dict)
        self.db.add(strength)
        await self.db.flush()
        await self.db.commit()

        created_id = strength.id
        self.db.expire(strength)
        return await self.strength_repository.get_by_id(created_id)

    async def update_strength(self, strength_id: int, strength_data: StrengthUpdate) -> Strength:
        strength = await self.strength_repository.get_by_id(strength_id)
        if not strength:
            raise NotFoundError("Strength not found")

        data = strength_data.model_dump(exclude_unset=True)
        for field, value in data.items():
            setattr(strength, field, value)

        await self.db.commit()

        updated_id = strength.id
        self.db.expire(strength)
        return await self.strength_repository.get_by_id(updated_id)

    async def delete_strength(self, strength_id: int) -> bool:
        return await self.strength_repository.delete(strength_id)
