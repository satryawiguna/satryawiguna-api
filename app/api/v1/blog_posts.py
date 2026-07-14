"""
Public Blog Post API endpoints (read-only, no auth)
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.blog import BlogPostResponse
from app.services.blog_service import BlogPostService
from app.utils.response import APIResponse, create_pagination_meta


router = APIRouter()


@router.get("", summary="Get all published blog posts (public)")
async def get_blog_posts(
    page: int = Query(1, ge=1),
    limit: Optional[int] = Query(10, ge=1, le=100),
    sortBy: str = Query("created_at"),
    sortOrder: str = Query("DESC"),
    keyword: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    service = BlogPostService(db)
    result = await service.get_blog_posts(
        page=page, limit=limit, sort_by=sortBy, sort_order=sortOrder,
        keyword=keyword, status="published",
    )
    posts_data = [BlogPostResponse.from_orm(post).model_dump() for post in result.items]
    if limit is None:
        return APIResponse.success(message="Blog posts retrieved successfully", data=posts_data)
    pagination = create_pagination_meta(result.total, result.page, result.limit)
    return APIResponse.success(message="Blog posts retrieved successfully", data=posts_data, pagination=pagination)


@router.get("/{post_id}", summary="Get a blog post by ID (public)")
async def get_blog_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = BlogPostService(db)
    post = await service.get_blog_post_by_id(post_id, published_only=True)
    if not post:
        return APIResponse.error(message="Blog post not found", status=status.HTTP_404_NOT_FOUND)
    return APIResponse.success(message="Blog post retrieved successfully", data=BlogPostResponse.from_orm(post).model_dump())

