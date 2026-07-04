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


# ---------------------------------------------------------------------------
# Swagger response example data
# ---------------------------------------------------------------------------
_EXPERIENCE_DATA = {
    "id": 1,
    "title": "Full Stack Developer",
    "company": "Explnc",
    "employment_type": "FULL_TIME",
    "description": "Built and scaled B2B and B2C platforms, improved user engagement and responsiveness.",
    "start_date": "2025-05-01",
    "end_date": None,
    "sort_order": 0,
    "created_at": "2026-05-30T00:00:00",
    "updated_at": "2026-05-30T00:00:00",
    "skills": [
        {"id": 1, "name": "Next.js", "icon_url": None},
        {"id": 2, "name": "Nest.js", "icon_url": None},
    ],
}

EXPERIENCES_LIST_EXAMPLES = {
    "with_pagination": {
        "summary": "With pagination (when limit is provided)",
        "description": "Response includes pagination metadata",
        "value": {
            "success": True,
            "status": 200,
            "message": "Experiences retrieved successfully",
            "data": [_EXPERIENCE_DATA],
            "pagination": {
                "total": 1,
                "page": 1,
                "limit": 10,
                "totalPages": 1,
                "hasNextPage": False,
                "hasPreviousPage": False,
            },
            "timestamp": "2026-05-30T00:00:00.000Z",
        },
    },
    "without_pagination": {
        "summary": "Without pagination (when limit is omitted)",
        "description": "Response without pagination metadata",
        "value": {
            "success": True,
            "status": 200,
            "message": "Experiences retrieved successfully",
            "data": [_EXPERIENCE_DATA],
            "timestamp": "2026-05-30T00:00:00.000Z",
        },
    },
}


@router.get(
    "",
    summary="Get all experiences (public)",
    description="""Get all experiences with optional pagination and filters.

**Pagination Options:**
- With pagination: Provide `limit` parameter (default: 10)
- Without pagination: Set `limit` to `null` to get all experiences

**Filters:**
- `keyword`: Search in title or company name
- `sortBy`: Field to sort by (default: sort_order)
- `sortOrder`: ASC or DESC (default: ASC)
""",
    responses={
        200: {
            "description": "Experiences retrieved successfully",
            "content": {"application/json": {"examples": EXPERIENCES_LIST_EXAMPLES}},
        }
    },
)
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
