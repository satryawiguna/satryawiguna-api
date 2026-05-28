"""
Admin Tags API endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.blog import TagCreate, TagUpdate, TagResponse
from app.services.category_tag_service import TagService
from app.utils.response import APIResponse, create_pagination_meta
from app.api.dependencies import get_current_user
from app.models.user import User


router = APIRouter()


# Response examples for Swagger
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
                "total": 1,
                "page": 1,
                "limit": 10,
                "totalPages": 1,
                "hasNextPage": False,
                "hasPreviousPage": False
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
    """,
    responses={
        200: {
            "description": "Tags retrieved successfully",
            "content": {"application/json": {"examples": TAGS_LIST_EXAMPLES}}
        }
    },
)
async def get_tags(
    page: int = Query(1, ge=1),
    limit: Optional[int] = Query(10, ge=1, le=100),
    sortBy: str = Query("name"),
    sortOrder: str = Query("ASC"),
    keyword: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TagService(db)
    result = await service.get_tags(page=page, limit=limit, sort_by=sortBy, sort_order=sortOrder)
    data = [TagResponse.from_orm(t).model_dump() for t in result.items]
    if limit is None:
        return APIResponse.success(message="Tags retrieved successfully", data=data)
    pagination = create_pagination_meta(result.total, result.page, result.limit)
    return APIResponse.success(message="Tags retrieved successfully", data=data, pagination=pagination)


@router.get(
    "/{tag_id}",
    summary="Get a tag by ID",
    responses={
        200: {
            "description": "Tag retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "status": 200,
                        "message": "Tag retrieved successfully",
                        "data": {
                            "id": 1,
                            "name": "python",
                            "slug": "python"
                        },
                        "timestamp": "2026-03-16T02:28:18.642Z"
                    }
                }
            }
        }
    }
)
async def get_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TagService(db)
    tag = await service.get_tag_by_id(tag_id)
    if not tag:
        return APIResponse.error(message="Tag not found", status=status.HTTP_404_NOT_FOUND)
    return APIResponse.success(message="Tag retrieved successfully", data=TagResponse.from_orm(tag).model_dump())


@router.post("", status_code=status.HTTP_201_CREATED, summary="Create a tag")
async def create_tag(
    data: TagCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TagService(db)
    tag = await service.create_tag(data)
    return APIResponse.success(
        message="Tag created successfully",
        status=status.HTTP_201_CREATED,
        data=TagResponse.from_orm(tag).model_dump()
    )


@router.put("/{tag_id}", summary="Update a tag")
async def update_tag(
    tag_id: int,
    data: TagUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TagService(db)
    tag = await service.update_tag(tag_id, data)
    return APIResponse.success(message="Tag updated successfully", data=TagResponse.from_orm(tag).model_dump())


@router.delete("/{tag_id}", summary="Delete a tag")
async def delete_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = TagService(db)
    await service.delete_tag(tag_id)
    return APIResponse.success(message="Tag deleted successfully")
