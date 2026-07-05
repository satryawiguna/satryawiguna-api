"""
Public Career Impacts API endpoints (read-only, no auth)
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.career_impact import CareerImpactResponse
from app.services.career_impact_service import CareerImpactService
from app.utils.response import APIResponse, create_pagination_meta


router = APIRouter()


# ---------------------------------------------------------------------------
# Swagger response example data
# ---------------------------------------------------------------------------
_CAREER_IMPACT_DATA = {
    "id": 1,
    "title": "Regional Full-Stack Role",
    "description": "Built cross-border event management systems for HK, MY, SG, PH, and ID with ReactJS and .NET Core backends.",
    "quote": "Scaling platforms for 500k+ daily active users",
    "icon_url": "https://cdn.satryawiguna.me/icons/globe.svg",
    "sort_order": 0,
    "created_at": "2026-07-04T00:00:00",
    "updated_at": "2026-07-04T00:00:00",
}

CAREER_IMPACTS_LIST_EXAMPLES = {
    "with_pagination": {
        "summary": "With pagination (when limit is provided)",
        "description": "Response includes pagination metadata",
        "value": {
            "success": True,
            "status": 200,
            "message": "Career impacts retrieved successfully",
            "data": [_CAREER_IMPACT_DATA],
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
            "message": "Career impacts retrieved successfully",
            "data": [_CAREER_IMPACT_DATA],
            "timestamp": "2026-07-04T00:00:00.000Z",
        },
    },
}


@router.get(
    "",
    summary="Get all career impacts (public)",
    description="""Get all career impacts with optional pagination and filters.

**Pagination Options:**
- With pagination: Provide `limit` parameter (default: 10)
- Without pagination: Set `limit` to `null` to get all career impacts

**Filters:**
- `keyword`: Search in title
- `sortBy`: Field to sort by (default: sort_order)
- `sortOrder`: ASC or DESC (default: ASC)
""",
    responses={
        200: {
            "description": "Career impacts retrieved successfully",
            "content": {"application/json": {"examples": CAREER_IMPACTS_LIST_EXAMPLES}},
        }
    },
)
async def get_career_impacts(
    page: int = Query(1, ge=1),
    limit: Optional[int] = Query(10, ge=1, le=100),
    sortBy: str = Query("sort_order"),
    sortOrder: str = Query("ASC"),
    keyword: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    service = CareerImpactService(db)
    result = await service.get_career_impacts(
        page=page,
        limit=limit,
        sort_by=sortBy,
        sort_order=sortOrder,
        keyword=keyword,
    )
    career_impacts_data = [CareerImpactResponse.from_orm(s).model_dump() for s in result.items]
    if limit is None:
        return APIResponse.success(message="Career impacts retrieved successfully", data=career_impacts_data)
    pagination = create_pagination_meta(result.total, result.page, result.limit)
    return APIResponse.success(
        message="Career impacts retrieved successfully",
        data=career_impacts_data,
        pagination=pagination,
    )
