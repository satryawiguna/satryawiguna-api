"""
Public Strengths API endpoints (read-only, no auth)
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.strength import StrengthResponse
from app.services.strength_service import StrengthService
from app.utils.response import APIResponse, create_pagination_meta


router = APIRouter()


# ---------------------------------------------------------------------------
# Swagger response example data
# ---------------------------------------------------------------------------
_STRENGTH_DATA = {
    "id": 1,
    "description": "System Architecture & Scalability",
    "sort_order": 0,
    "created_at": "2026-07-04T00:00:00",
    "updated_at": "2026-07-04T00:00:00",
}

STRENGTHS_LIST_EXAMPLES = {
    "with_pagination": {
        "summary": "With pagination (when limit is provided)",
        "description": "Response includes pagination metadata",
        "value": {
            "success": True,
            "status": 200,
            "message": "Strengths retrieved successfully",
            "data": [_STRENGTH_DATA],
            "pagination": {
                "total": 1,
                "page": 1,
                "limit": 10,
                "totalPages": 1,
                "hasNextPage": False,
                "hasPreviousPage": False,
            },
            "timestamp": "2026-07-04T00:00:00.000Z",
        },
    },
    "without_pagination": {
        "summary": "Without pagination (when limit is omitted)",
        "description": "Response without pagination metadata",
        "value": {
            "success": True,
            "status": 200,
            "message": "Strengths retrieved successfully",
            "data": [_STRENGTH_DATA],
            "timestamp": "2026-07-04T00:00:00.000Z",
        },
    },
}


@router.get(
    "",
    summary="Get all strengths (public)",
    description="""Get all strengths with optional pagination and filters.

**Pagination Options:**
- With pagination: Provide `limit` parameter (default: 10)
- Without pagination: Set `limit` to `null` to get all strengths

**Filters:**
- `keyword`: Search in description
- `sortBy`: Field to sort by (default: sort_order)
- `sortOrder`: ASC or DESC (default: ASC)
""",
    responses={
        200: {
            "description": "Strengths retrieved successfully",
            "content": {"application/json": {"examples": STRENGTHS_LIST_EXAMPLES}},
        }
    },
)
async def get_strengths(
    page: int = Query(1, ge=1),
    limit: Optional[int] = Query(10, ge=1, le=100),
    sortBy: str = Query("sort_order"),
    sortOrder: str = Query("ASC"),
    keyword: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    service = StrengthService(db)
    result = await service.get_strengths(
        page=page,
        limit=limit,
        sort_by=sortBy,
        sort_order=sortOrder,
        keyword=keyword,
    )
    strengths_data = [StrengthResponse.from_orm(s).model_dump() for s in result.items]
    if limit is None:
        return APIResponse.success(message="Strengths retrieved successfully", data=strengths_data)
    pagination = create_pagination_meta(result.total, result.page, result.limit)
    return APIResponse.success(
        message="Strengths retrieved successfully",
        data=strengths_data,
        pagination=pagination,
    )
