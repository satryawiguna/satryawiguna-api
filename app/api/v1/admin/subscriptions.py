"""
Admin Subscription API endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.subscription import SubscriptionResponse
from app.services.subscription_service import SubscriptionService
from app.utils.response import APIResponse, create_pagination_meta
from app.api.dependencies import get_current_user
from app.models.user import User


router = APIRouter()


@router.get(
    "",
    summary="Get all subscriptions",
    description="""Get all subscriptions with optional pagination and filters.

**Pagination Options:**
- With pagination: Provide `limit` parameter (default: 10)
- Without pagination: Set `limit` to `null` to get all subscriptions

**Filters:**
- `keyword`: Search in email
- `sortBy`: Field to sort by (default: created_at)
- `sortOrder`: ASC or DESC (default: DESC)
""",
)
async def get_subscriptions(
    page: int = Query(1, ge=1, description="Page number"),
    limit: Optional[int] = Query(10, ge=1, le=100, description="Items per page. Set to null for all subscriptions"),
    sortBy: str = Query("created_at", description="Sort field"),
    sortOrder: str = Query("DESC", description="Sort order (ASC or DESC)"),
    keyword: Optional[str] = Query(None, description="Search keyword for email"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = SubscriptionService(db)
    result = await service.get_subscriptions(
        page=page,
        limit=limit,
        sort_by=sortBy,
        sort_order=sortOrder,
        keyword=keyword,
    )
    subscriptions_data = [SubscriptionResponse.model_validate(s).model_dump() for s in result.items]
    if limit is None:
        return APIResponse.success(message="Subscriptions retrieved successfully", data=subscriptions_data)
    pagination = create_pagination_meta(result.total, result.page, result.limit)
    return APIResponse.success(
        message="Subscriptions retrieved successfully",
        data=subscriptions_data,
        pagination=pagination,
    )
