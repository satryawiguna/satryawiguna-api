"""
Subscription service for newsletter subscription business logic
"""
import logging
import secrets
from typing import Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, DuplicateError
from app.core.config import settings
from app.models.subscription import Subscription
from app.repositories.subscription_repository import SubscriptionRepository
from app.utils.email import send_verification_email
from app.utils.pagination import PaginatedResult

logger = logging.getLogger(__name__)


class SubscriptionService:
    """Service for subscription-related business logic"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.subscription_repository = SubscriptionRepository(db)

    async def subscribe(self, email: str) -> dict:
        """
        Initiate subscription for an email address.

        - If email is already verified and not unsubscribed, return existing.
        - If email exists but is unsubscribed, create a fresh record.
        - Otherwise, create a pending record with a verification token and send email.

        Returns dict with message and whether email was sent.
        """
        existing = await self.subscription_repository.get_by_email(email)

        if existing and existing.verified_at and not existing.unsubscribed_at:
            # Already active — no need to re-send
            raise DuplicateError("Email is already subscribed")

        if existing and existing.verified_at and existing.unsubscribed_at:
            # Previously unsubscribed — create a fresh record
            await self.db.delete(existing)
            await self.db.flush()

        # Generate verification token
        verification_token = secrets.token_urlsafe(64)

        subscription = Subscription(
            email=email,
            verification_token=verification_token,
            verified_at=None,
            unsubscribed_at=None,
            subscribed_at=datetime.utcnow(),
        )
        self.db.add(subscription)
        await self.db.flush()
        await self.db.commit()

        # Build frontend-facing verification URL
        verification_url = (
            f"{settings.FRONTEND_URL}/subscriptions/verify?token={verification_token}"
        )

        # Send verification email (fire-and-forget)
        email_sent = await send_verification_email(email, verification_url)

        if not email_sent:
            logger.warning(f"Verification email failed to send to {email}")

        return {
            "email": email,
            "email_sent": email_sent,
        }

    async def verify_subscription(self, token: str) -> Subscription:
        """
        Verify a subscription by token.

        Finds the subscription by verification token, sets verified_at,
        and clears the token. Raises NotFoundError if token is invalid
        or subscription is already verified.
        """
        subscription = await self.subscription_repository.get_by_verification_token(token)

        if not subscription:
            raise NotFoundError("Invalid or expired verification token")

        if subscription.verified_at:
            raise DuplicateError("Email is already verified")

        subscription.verified_at = datetime.utcnow()
        subscription.verification_token = None

        await self.db.commit()

        # Expire and re-fetch to get clean state
        self.db.expire(subscription)
        refreshed = await self.subscription_repository.get_by_id(subscription.id)
        return refreshed

    async def unsubscribe(self, email: str) -> None:
        """
        Unsubscribe an email.

        Finds the verified subscription and sets unsubscribed_at.
        Raises NotFoundError if no verified subscription exists.
        """
        subscription = await self.subscription_repository.get_by_email(email)

        if not subscription or not subscription.verified_at:
            raise NotFoundError("No active subscription found for this email")

        if subscription.unsubscribed_at:
            raise DuplicateError("Email is already unsubscribed")

        subscription.unsubscribed_at = datetime.utcnow()

        await self.db.commit()

    async def get_subscriptions(
        self,
        page: int = 1,
        limit: Optional[int] = 10,
        sort_by: str = "created_at",
        sort_order: str = "DESC",
        keyword: Optional[str] = None,
    ) -> PaginatedResult:
        """Get paginated list of all subscriptions (admin)."""
        return await self.subscription_repository.get_paginated(
            page=page,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order,
            keyword=keyword,
        )
