"""
Public Experiences API endpoints (read-only, no auth)
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.experience import ExperienceResponse
from app.services.experience_service import ExperienceService
from app.utils.response import APIResponse, create_pagination_meta


router = APIRouter()


@router.get("", summary="Get all experiences (public)")
async def get_experiences(
    page: int = Query(1, ge=1),
    limit: Optional[int] = Query(10, ge=1, le=100),
    sortBy: str = Query("sort_order"),
    sortOrder: str = Query("ASC"),
    keyword: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    service = ExperienceService(db)
    result = await service.get_experiences(
        page=page,
        limit=limit,
        sort_by=sortBy,
        sort_order=sortOrder,
        keyword=keyword,
    )
    experiences_data = [ExperienceResponse.from_orm(e).model_dump() for e in result.items]
    if limit is None:
        return APIResponse.success(message="Experiences retrieved successfully", data=experiences_data)
    pagination = create_pagination_meta(result.total, result.page, result.limit)
    return APIResponse.success(
        message="Experiences retrieved successfully",
        data=experiences_data,
        pagination=pagination,
    )
