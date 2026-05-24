"""
Admin Categories API endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.blog import CategoryCreate, CategoryUpdate, CategoryResponse
from app.services.category_tag_service import CategoryService
from app.utils.response import APIResponse, create_pagination_meta
from app.api.dependencies import get_current_user
from app.models.user import User


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
    description="Get all categories with optional pagination and filters.",
    responses={
        200: {
            "description": "Categories retrieved successfully",
            "content": {"application/json": {"examples": CATEGORIES_LIST_EXAMPLES}}
        }
    }
)
async def get_categories(
    page: int = Query(1, ge=1),
    limit: Optional[int] = Query(None, ge=1, le=100),
    sortBy: str = Query("name"),
    sortOrder: str = Query("ASC"),
    keyword: Optional[str] = Query(None, description="Filter categories by keyword (matches name and slug)"),
    type: Optional[str] = Query(None, description="Filter categories by type (BLOG_POST, PROJECT, or SKILL)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CategoryService(db)
    result = await service.get_categories(page=page, limit=limit, sort_by=sortBy, sort_order=sortOrder, keyword=keyword, type=type)
    data = [CategoryResponse.from_orm(c).model_dump() for c in result.items]
    if limit is None:
        return APIResponse.success(message="Categories retrieved successfully", data=data)
    pagination = create_pagination_meta(result.total, result.page, result.limit)
    return APIResponse.success(message="Categories retrieved successfully", data=data, pagination=pagination)


@router.get(
    "/{category_id}",
    summary="Get a category by ID",
    responses={
        200: {
            "description": "Category retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "status": 200,
                        "message": "Category retrieved successfully",
                        "data": {
                            "id": 1,
                            "name": "Technology",
                            "slug": "technology",
                            "type": "BLOG_POST"
                        },
                        "timestamp": "2026-03-16T02:28:18.642Z"
                    }
                }
            }
        }
    }
)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CategoryService(db)
    category = await service.get_category_by_id(category_id)
    if not category:
        return APIResponse.error(message="Category not found", status=status.HTTP_404_NOT_FOUND)
    return APIResponse.success(message="Category retrieved successfully", data=CategoryResponse.from_orm(category).model_dump())


@router.post("", status_code=status.HTTP_201_CREATED, summary="Create a category")
async def create_category(
    data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CategoryService(db)
    category = await service.create_category(data)
    return APIResponse.success(
        message="Category created successfully",
        status=status.HTTP_201_CREATED,
        data=CategoryResponse.from_orm(category).model_dump()
    )


@router.put("/{category_id}", summary="Update a category")
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CategoryService(db)
    category = await service.update_category(category_id, data)
    return APIResponse.success(message="Category updated successfully", data=CategoryResponse.from_orm(category).model_dump())


@router.delete("/{category_id}", summary="Delete a category")
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CategoryService(db)
    await service.delete_category(category_id)
    return APIResponse.success(message="Category deleted successfully")
