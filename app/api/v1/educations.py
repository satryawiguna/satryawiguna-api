"""
Public Educations API endpoints (read-only, no auth)
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.education import EducationResponse
from app.services.education_service import EducationService
from app.utils.response import APIResponse, create_pagination_meta


router = APIRouter()


# ---------------------------------------------------------------------------
# Swagger response example data
# ---------------------------------------------------------------------------
_EDUCATION_DATA = {
    "id": 1,
    "degree": "Bachelor of Electrical Engineering",
    "institution": "Udayana University",
    "start_year": 2001,
    "end_year": 2006,
    "sort_order": 0,
    "created_at": "2026-05-30T00:00:00",
    "updated_at": "2026-05-30T00:00:00",
}

EDUCATIONS_LIST_EXAMPLES = {
    "with_pagination": {
        "summary": "With pagination (when limit is provided)",
        "description": "Response includes pagination metadata",
        "value": {
            "success": True,
            "status": 200,
            "message": "Educations retrieved successfully",
            "data": [_EDUCATION_DATA],
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
            "message": "Educations retrieved successfully",
            "data": [_EDUCATION_DATA],
            "timestamp": "2026-05-30T00:00:00.000Z",
        },
    },
}


@router.get(
    "",
    summary="Get all educations (public)",
    description="""Get all educations with optional pagination and filters.

**Pagination Options:**
- With pagination: Provide `limit` parameter (default: 10)
- Without pagination: Set `limit` to `null` to get all educations

**Filters:**
- `keyword`: Search in degree or institution name
- `sortBy`: Field to sort by (default: sort_order)
- `sortOrder`: ASC or DESC (default: ASC)
""",
    responses={
        200: {
            "description": "Educations retrieved successfully",
            "content": {"application/json": {"examples": EDUCATIONS_LIST_EXAMPLES}},
        }
    },
)
async def get_educations(
    page: int = Query(1, ge=1),
    limit: Optional[int] = Query(10, ge=1, le=100),
    sortBy: str = Query("sort_order"),
    sortOrder: str = Query("ASC"),
    keyword: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    service = EducationService(db)
    result = await service.get_educations(
        page=page,
        limit=limit,
        sort_by=sortBy,
        sort_order=sortOrder,
        keyword=keyword,
    )
    educations_data = [EducationResponse.from_orm(e).model_dump() for e in result.items]
    if limit is None:
        return APIResponse.success(message="Educations retrieved successfully", data=educations_data)
    pagination = create_pagination_meta(result.total, result.page, result.limit)
    return APIResponse.success(
        message="Educations retrieved successfully",
        data=educations_data,
        pagination=pagination,
    )
