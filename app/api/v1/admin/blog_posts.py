"""
Admin Blog Post API endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.blog import BlogPostCreate, BlogPostUpdate, BlogPostResponse
from app.services.blog_service import BlogPostService
from app.utils.response import APIResponse, create_pagination_meta
from app.api.dependencies import get_current_user
from app.models.user import User


router = APIRouter()

_BLOG_POST_DATA = {
    "id": 1,
    "title": "Getting Started with FastAPI",
    "slug": "getting-started-with-fastapi",
    "excerpt": "Learn how to build modern APIs with FastAPI",
    "content": "FastAPI is a modern, fast web framework...",
    "thumbnail_url": "https://example.com/images/fastapi-thumb.jpg",
    "image_url": "https://example.com/images/fastapi.jpg",
    "status": "published",
    "author_id": 1,
    "published_at": "2026-03-15T00:00:00",
    "created_at": "2026-03-15T22:22:19",
    "updated_at": "2026-03-15T22:22:19"
}

BLOG_POSTS_LIST_EXAMPLES = {
    "with_pagination": {
        "summary": "With pagination (when limit is provided)",
        "description": "Response includes pagination metadata",
        "value": {
            "success": True,
            "status": 200,
            "message": "Blog posts retrieved successfully",
            "data": [_BLOG_POST_DATA],
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
            "message": "Blog posts retrieved successfully",
            "data": [_BLOG_POST_DATA],
            "timestamp": "2026-03-16T02:28:18.642Z"
        }
    }
}

BLOG_POST_SINGLE_EXAMPLE = {
    "success": True,
    "status": 200,
    "message": "Blog post retrieved successfully",
    "data": {
        "id": 1,
        "title": "Getting Started with FastAPI",
        "slug": "getting-started-with-fastapi",
        "excerpt": "Learn how to build modern APIs with FastAPI",
        "content": "FastAPI is a modern, fast web framework...",
        "thumbnail_url": "https://example.com/images/fastapi-thumb.jpg",
        "image_url": "https://example.com/images/fastapi.jpg",
        "status": "published",
        "author_id": 1,
        "published_at": "2026-03-15T00:00:00",
        "created_at": "2026-03-15T22:22:19",
        "updated_at": "2026-03-15T22:22:19",
        "categories": [{"id": 1, "name": "Tech", "slug": "tech", "type": "BLOG_POST"}],
        "tags": [{"id": 1, "name": "python", "slug": "python"}]
    },
    "timestamp": "2026-03-16T02:28:18.642Z"
}



@router.get(
    "",
    summary="Get all blog posts",
    description="Get all blog posts with optional pagination, keyword search, status, author, category, and tag filters.",
    responses={
        200: {
            "description": "Blog posts retrieved successfully",
            "content": {"application/json": {"examples": BLOG_POSTS_LIST_EXAMPLES}}
        }
    }
)
async def get_blog_posts(
    page: int = Query(1, ge=1),
    limit: Optional[int] = Query(10, ge=1, le=100),
    sortBy: str = Query("created_at"),
    sortOrder: str = Query("DESC"),
    keyword: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    author_id: Optional[int] = Query(None),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    tag_id: Optional[int] = Query(None, description="Filter by tag ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = BlogPostService(db)
    result = await service.get_blog_posts(
        page=page, limit=limit, sort_by=sortBy, sort_order=sortOrder,
        keyword=keyword, status=status_filter, author_id=author_id,
        category_id=category_id, tag_id=tag_id,
    )
    posts_data = [BlogPostResponse.from_orm(post).model_dump() for post in result.items]
    if limit is None:
        return APIResponse.success(message="Blog posts retrieved successfully", data=posts_data)
    pagination = create_pagination_meta(result.total, result.page, result.limit)
    return APIResponse.success(message="Blog posts retrieved successfully", data=posts_data, pagination=pagination)


@router.get(
    "/{post_id}",
    summary="Get a blog post by ID",
    responses={
        200: {"description": "Blog post retrieved successfully", "content": {"application/json": {"example": BLOG_POST_SINGLE_EXAMPLE}}},
        404: {"description": "Blog post not found"}
    }
)
async def get_blog_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = BlogPostService(db)
    post = await service.get_blog_post_by_id(post_id)
    if not post:
        return APIResponse.error(message="Blog post not found", status=status.HTTP_404_NOT_FOUND)
    return APIResponse.success(message="Blog post retrieved successfully", data=BlogPostResponse.from_orm(post).model_dump())


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create a blog post",
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "example": {
                        "title": "Getting Started with FastAPI",
                        "slug": "getting-started-with-fastapi",
                        "excerpt": "Learn how to build modern APIs with FastAPI",
                        "content": "FastAPI is a modern, fast web framework...",
                        "thumbnail_url": "https://example.com/thumb.jpg",
                        "image_url": "https://example.com/image.jpg",
                        "status": "draft",
                        "author_id": 1,
                        "category_ids": [1, 2],
                        "tag_ids": [1]
                    }
                }
            }
        }
    }
)
async def create_blog_post(
    post_data: BlogPostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Default author_id to the authenticated user if not provided
    if post_data.author_id is None:
        post_data.author_id = current_user.id
    service = BlogPostService(db)
    post = await service.create_blog_post(post_data)
    return APIResponse.success(
        message="Blog post created successfully",
        status=status.HTTP_201_CREATED,
        data=BlogPostResponse.from_orm(post).model_dump()
    )


@router.put("/{post_id}", summary="Update a blog post")
async def update_blog_post(
    post_id: int,
    post_data: BlogPostUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = BlogPostService(db)
    post = await service.update_blog_post(post_id, post_data)
    return APIResponse.success(message="Blog post updated successfully", data=BlogPostResponse.from_orm(post).model_dump())


@router.delete("/{post_id}", summary="Delete a blog post")
async def delete_blog_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = BlogPostService(db)
    await service.delete_blog_post(post_id)
    return APIResponse.success(message="Blog post deleted successfully")
