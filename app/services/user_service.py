"""
User service for user-related business logic
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, DuplicateError
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.repositories.user_repository import UserRepository, RoleRepository
from app.core.security import hash_password
from app.utils.pagination import PaginatedResult


class UserService:
    """Service for user-related business logic"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repository = UserRepository(db)
        self.role_repository = RoleRepository(db)

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        return await self.user_repository.get_by_id(user_id)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        return await self.user_repository.get_by_email(email)

    async def get_users(
        self,
        page: int = 1,
        limit: Optional[int] = 10,
        sort_by: str = "created_at",
        sort_order: str = "DESC",
        keyword: Optional[str] = None,
    ) -> PaginatedResult:
        return await self.user_repository.get_paginated(
            page=page,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
            keyword=keyword,
        )

    async def create_user(self, user_data: UserCreate) -> User:
        existing_user = await self.user_repository.get_by_email(user_data.email)
        if existing_user:
            raise DuplicateError("Email already registered")

        user = User(
            name=user_data.name,
            email=user_data.email,
            password=hash_password(user_data.password),
        )
        return await self.user_repository.create(user)

    async def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")

        if user_data.name is not None:
            user.name = user_data.name
        if user_data.phone is not None:
            user.phone = user_data.phone
        if user_data.avatar_url is not None:
            user.avatar_url = user_data.avatar_url

        return await self.user_repository.update(user)

    async def delete_user(self, user_id: int) -> bool:
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        return await self.user_repository.delete(user_id)
