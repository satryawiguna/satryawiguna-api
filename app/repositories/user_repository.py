"""
User repository for user-specific database operations
"""
from typing import Optional, List

from sqlalchemy import select, desc, asc, or_, update as sql_update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User, Role, UserRole, RefreshToken
from app.repositories.base import BaseRepository
from app.utils.pagination import PaginatedResult, paginate_async


class UserRepository(BaseRepository[User]):
    """Repository for User model"""

    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_id(self, id: int) -> Optional[User]:
        """Get user by ID with roles eagerly loaded."""
        result = await self.db.execute(
            select(User)
            .where(User.id == id)
            .options(selectinload(User.user_roles).selectinload(UserRole.role))
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email with roles eagerly loaded."""
        result = await self.db.execute(
            select(User)
            .where(User.email == email)
            .options(selectinload(User.user_roles).selectinload(UserRole.role))
        )
        return result.scalar_one_or_none()

    async def get_paginated(
        self,
        page: int = 1,
        limit: Optional[int] = 10,
        sort_by: str = "created_at",
        sort_order: str = "DESC",
        keyword: Optional[str] = None,
        **filters,
    ) -> PaginatedResult:
        sort_column = getattr(User, sort_by, User.id)
        order = desc(sort_column) if sort_order.upper() == "DESC" else asc(sort_column)
        stmt = select(User).order_by(order)

        if keyword:
            pattern = f"%{keyword}%"
            stmt = stmt.where(or_(User.name.ilike(pattern), User.email.ilike(pattern)))

        return await paginate_async(self.db, stmt, page=page, limit=limit)


class RoleRepository(BaseRepository[Role]):
    """Repository for Role model"""

    def __init__(self, db: AsyncSession):
        super().__init__(Role, db)

    async def get_by_name(self, name: str) -> Optional[Role]:
        result = await self.db.execute(select(Role).where(Role.name == name))
        return result.scalar_one_or_none()


class UserRoleRepository(BaseRepository[UserRole]):
    """Repository for UserRole model"""

    def __init__(self, db: AsyncSession):
        super().__init__(UserRole, db)

    async def get_user_roles(self, user_id: int) -> List[Role]:
        result = await self.db.execute(
            select(UserRole)
            .where(UserRole.user_id == user_id)
            .options(selectinload(UserRole.role))
        )
        return [ur.role for ur in result.scalars().all()]

    async def assign_role(self, user_id: int, role_id: int) -> UserRole:
        user_role = UserRole(user_id=user_id, role_id=role_id)
        return await self.create(user_role)

    async def remove_role(self, user_id: int, role_id: int) -> bool:
        result = await self.db.execute(
            select(UserRole).where(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id,
            )
        )
        user_role = result.scalar_one_or_none()
        if user_role:
            await self.db.delete(user_role)
            await self.db.commit()
            return True
        return False


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    """Repository for RefreshToken model"""

    def __init__(self, db: AsyncSession):
        super().__init__(RefreshToken, db)

    async def find_by_token(self, token: str) -> Optional[RefreshToken]:
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.token == token)
        )
        return result.scalar_one_or_none()

    async def revoke(self, token: str) -> bool:
        """Mark a single token as revoked. Returns False if not found."""
        record = await self.find_by_token(token)
        if not record:
            return False
        record.revoked = True
        await self.db.commit()
        return True

    async def revoke_all_for_user(self, user_id: int) -> None:
        """Bulk-revoke all active refresh tokens for a user (e.g. on password change)."""
        await self.db.execute(
            sql_update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.revoked == False)  # noqa: E712
            .values(revoked=True)
        )
        await self.db.commit()

