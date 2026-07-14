"""
Public Subscription API endpoints (no auth required)
"""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.subscription import SubscribeRequest, UnsubscribeRequest, SubscriptionResponse
from app.services.subscription_service import SubscriptionService
from app.utils.response import APIResponse


router = APIRouter()


@router.post(
    "",
    summary="Subscribe to newsletter",
    description="""Submit an email address to subscribe to the newsletter.

    A verification email will be sent to the provided email address.
    The subscription is only activated after clicking the verification link.

    **Note:** The verification link in the email points to the frontend app,
    which then calls the API verify endpoint internally.
    """,
)
async def subscribe(
    request: SubscribeRequest,
    db: AsyncSession = Depends(get_db),
):
    service = SubscriptionService(db)
    result = await service.subscribe(request.email)
    return APIResponse.success(
        message="Verification email sent. Please check your inbox.",
        data=result,
    )


@router.get(
    "/verify",
    summary="Verify subscription email",
    description="""Verify a subscription by its token.

    This endpoint is called by the frontend after the user clicks the
    verification link in the email. The token is passed as a query param.
    """,
)
async def verify_subscription(
    token: str = Query(..., description="Verification token from email"),
    db: AsyncSession = Depends(get_db),
):
    service = SubscriptionService(db)
    subscription = await service.verify_subscription(token)
    return APIResponse.success(
        message="Subscription verified successfully",
        data=SubscriptionResponse.model_validate(subscription).model_dump(),
    )


@router.post(
    "/unsubscribe",
    summary="Unsubscribe from newsletter",
    description="""Unsubscribe an email address from the newsletter.

    Requires the email address that was used to subscribe.
    """,
)
async def unsubscribe(
    request: UnsubscribeRequest,
    db: AsyncSession = Depends(get_db),
):
    service = SubscriptionService(db)
    await service.unsubscribe(request.email)
    return APIResponse.success(
        message="Unsubscribed successfully",
    )
