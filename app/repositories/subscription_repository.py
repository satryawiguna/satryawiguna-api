"""
Subscription repository for subscription-specific database operations
"""
from typing import Optional

from sqlalchemy import select, desc, asc, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subscription import Subscription
from app.repositories.base import BaseRepository
from app.utils.pagination import PaginatedResult, paginate_async


class SubscriptionRepository(BaseRepository[Subscription]):
    """Repository for Subscription model"""

    def __init__(self, db: AsyncSession):
        super().__init__(Subscription, db)

    async def get_by_email(self, email: str) -> Optional[Subscription]:
        """Get subscription by email."""
        result = await self.db.execute(
            select(Subscription).where(Subscription.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_verification_token(self, token: str) -> Optional[Subscription]:
        """Get subscription by verification token."""
        result = await self.db.execute(
            select(Subscription).where(Subscription.verification_token == token)
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
        sort_column = getattr(Subscription, sort_by, Subscription.id)
        order = desc(sort_column) if sort_order.upper() == "DESC" else asc(sort_column)
        stmt = select(Subscription).order_by(order)

        if keyword:
            pattern = f"%{keyword}%"
            stmt = stmt.where(
                or_(Subscription.email.ilike(pattern))
            )

        return await paginate_async(self.db, stmt, page=page, limit=limit)
