"""
Public Tags API endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.blog import TagResponse
from app.services.category_tag_service import TagService
from app.utils.response import APIResponse, create_pagination_meta


router = APIRouter()


_TAG_DATA = {
    "id": 1,
    "name": "python",
    "slug": "python"
}

TAGS_LIST_EXAMPLES = {
    "with_pagination": {
        "summary": "With pagination (when limit is provided)",
        "description": "Response includes pagination metadata",
        "value": {
            "success": True,
            "status": 200,
            "message": "Tags retrieved successfully",
            "data": [_TAG_DATA],
            "pagination": {
                "total": 1, "page": 1, "limit": 10,
                "totalPages": 1, "hasNextPage": False, "hasPreviousPage": False
            },
            "timestamp": "2026-03-16T02:28:18.642Z"
        }
    },
    "without_pagination": {
        "summary": "Without pagination (when limit is omitted)",
        "description": "Response without pagination metadata",
        "value": {
            "success": True,
            "status": 200,
            "message": "Tags retrieved successfully",
            "data": [_TAG_DATA],
            "timestamp": "2026-03-16T02:28:18.642Z"
        }
    }
}


@router.get(
    "",
    summary="Get all tags",
    description="""Get all tags with optional pagination.

    **Pagination Options:**
    - With pagination: Provide `limit` parameter (default: 10)
    - Without pagination: Set `limit` to `null` to get all tags

    **Filters:**
    - `keyword`: Search in name and slug
    - `sortBy`: Field to sort by (default: name)
    - `sortOrder`: ASC or DESC (default: ASC)
    """,
    responses={
        200: {
            "description": "Tags retrieved successfully",
            "content": {"application/json": {"examples": TAGS_LIST_EXAMPLES}}
        }
    }
)
async def get_tags(
    page: int = Query(1, ge=1, description="Page number (only used when limit is provided)"),
    limit: Optional[int] = Query(10, ge=1, le=100, description="Items per page. Set to null for all tags without pagination"),
    sortBy: str = Query("name", description="Sort field"),
    sortOrder: str = Query("ASC", description="Sort order (ASC or DESC)"),
    keyword: Optional[str] = Query(None, description="Search keyword (matches name and slug)"),
    db: AsyncSession = Depends(get_db),
):
    service = TagService(db)
    result = await service.get_tags(
        page=page,
        limit=limit,
        sort_by=sortBy,
        sort_order=sortOrder,
    )
    data = [TagResponse.from_orm(t).model_dump() for t in result.items]
    if limit is None:
        return APIResponse.success(message="Tags retrieved successfully", data=data)
    pagination = create_pagination_meta(result.total, result.page, result.limit)
    return APIResponse.success(message="Tags retrieved successfully", data=data, pagination=pagination)
