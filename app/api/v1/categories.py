"""
Public Categories API endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.blog import CategoryResponse
from app.services.category_tag_service import CategoryService
from app.utils.response import APIResponse, create_pagination_meta


router = APIRouter()


_CATEGORY_DATA = {
    "id": 1,
    "name": "Technology",
    "slug": "technology",
    "type": "BLOG_POST"
}

CATEGORIES_LIST_EXAMPLES = {
    "with_pagination": {
        "summary": "With pagination (when limit is provided)",
        "description": "Response includes pagination metadata",
        "value": {
            "success": True,
            "status": 200,
            "message": "Categories retrieved successfully",
            "data": [_CATEGORY_DATA],
            "pagination": {
                "total": 1, "page": 1, "limit": 10,
                "totalPages": 1, "hasNextPage": False, "hasPreviousPage": False
            },
            "timestamp": "2026-03-16T00:00:00.000Z"
        }
    },
    "without_pagination": {
        "summary": "Without pagination (when limit is omitted)",
        "description": "Response without pagination metadata",
        "value": {
            "success": True,
            "status": 200,
            "message": "Categories retrieved successfully",
            "data": [_CATEGORY_DATA],
            "timestamp": "2026-03-16T00:00:00.000Z"
        }
    }
}


@router.get(
    "",
    summary="Get all categories",
    description="""Get all categories with optional pagination and filters.

    **Pagination Options:**
    - With pagination: Provide `limit` parameter (default: 10)
    - Without pagination: Set `limit` to `null` to get all categories

    **Filters:**
    - `keyword`: Search in name and slug
    - `type`: Filter by type (BLOG_POST, PROJECT, or SKILL)
    - `sortBy`: Field to sort by (default: name)
    - `sortOrder`: ASC or DESC (default: ASC)
    """,
    responses={
        200: {
            "description": "Categories retrieved successfully",
            "content": {"application/json": {"examples": CATEGORIES_LIST_EXAMPLES}}
        }
    }
)
async def get_categories(
    page: int = Query(1, ge=1, description="Page number (only used when limit is provided)"),
    limit: Optional[int] = Query(10, ge=1, le=100, description="Items per page. Set to null for all categories without pagination"),
    sortBy: str = Query("name", description="Sort field"),
    sortOrder: str = Query("ASC", description="Sort order (ASC or DESC)"),
    keyword: Optional[str] = Query(None, description="Search keyword (matches name and slug)"),
    type: Optional[str] = Query(None, description="Filter by type (BLOG_POST, PROJECT, or SKILL)"),
    db: AsyncSession = Depends(get_db),
):
    service = CategoryService(db)
    result = await service.get_categories(
        page=page,
        limit=limit,
        sort_by=sortBy,
        sort_order=sortOrder,
        keyword=keyword,
        type=type,
    )
    data = [CategoryResponse.from_orm(c).model_dump() for c in result.items]
    if limit is None:
        return APIResponse.success(message="Categories retrieved successfully", data=data)
    pagination = create_pagination_meta(result.total, result.page, result.limit)
    return APIResponse.success(message="Categories retrieved successfully", data=data, pagination=pagination)
