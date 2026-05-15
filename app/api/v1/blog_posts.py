"""
Blog post API endpoints
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


# Response examples for Swagger
BLOG_POSTS_LIST_EXAMPLES = {
    "with_pagination": {
        "summary": "With pagination (when limit is provided)",
        "description": "Response includes pagination metadata",
        "value": {
            "success": True,
            "status": 200,
            "message": "Blog posts retrieved successfully",
            "data": [
                {
                    "title": "Getting Started with FastAPI",
                    "slug": "getting-started-with-fastapi",
                    "excerpt": "Learn how to build modern APIs with FastAPI",
                    "content": "FastAPI is a modern, fast web framework...",
                    "featured_image_url": "https://example.com/images/fastapi.jpg",
                    "status": "published",
                    "id": 1,
                    "author_id": 1,
                    "published_at": "2026-03-15T00:00:00",
                    "created_at": "2026-03-15T22:22:19",
                    "updated_at": "2026-03-15T22:22:19"
                }
            ],
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
            "message": "Blog posts retrieved successfully",
            "data": [
                {
                    "title": "Getting Started with FastAPI",
                    "slug": "getting-started-with-fastapi",
                    "excerpt": "Learn how to build modern APIs with FastAPI",
                    "content": "FastAPI is a modern, fast web framework...",
                    "featured_image_url": "https://example.com/images/fastapi.jpg",
                    "status": "published",
                    "id": 1,
                    "author_id": 1,
                    "published_at": "2026-03-15T00:00:00",
                    "created_at": "2026-03-15T22:22:19",
                    "updated_at": "2026-03-15T22:22:19"
                }
            ],
            "timestamp": "2026-03-16T02:28:18.642Z"
        }
    }
}


router = APIRouter()


@router.get(
    "",
    summary="Get all blog posts",
    description="""Get all blog posts with optional pagination and filters.
    
    **Pagination Options:**
    - With pagination: Provide `limit` parameter (default: 10)
    - Without pagination: Set `limit` to `null` to get all blog posts
    
    **Filters:**
    - `keyword`: Search in title or excerpt
    - `status`: Filter by status (draft, published, etc.)
    - `author_id`: Filter by author
    - `sortBy`: Field to sort by (default: created_at)
    - `sortOrder`: ASC or DESC (default: DESC)
    """,
    responses={
        200: {
            "description": "Blog posts retrieved successfully",
            "content": {
                "application/json": {
                    "examples": BLOG_POSTS_LIST_EXAMPLES
                }
            }
        }
    }
)
async def get_blog_posts(
    page: int = Query(1, ge=1, description="Page number (only used when limit is provided)"),
    limit: Optional[int] = Query(10, ge=1, le=100, description="Items per page. Set to null for all blog posts without pagination"),
    sortBy: str = Query("created_at", description="Sort field"),
    sortOrder: str = Query("DESC", description="Sort order (ASC or DESC)"),
    keyword: Optional[str] = Query(None, description="Search keyword for title or excerpt"),
    status: Optional[str] = Query(None, description="Filter by status (draft, published, etc.)"),
    author_id: Optional[int] = Query(None, description="Filter by author ID"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all blog posts with optional pagination and filters.
    
    Returns list of blog posts with or without pagination based on limit parameter.
    """
    service = BlogPostService(db)
    result = await service.get_blog_posts(
        page=page,
        limit=limit,
        sort_by=sortBy,
        sort_order=sortOrder,
        keyword=keyword,
        status=status,
        author_id=author_id,
    )

    posts_data = [BlogPostResponse.from_orm(post).model_dump() for post in result.items]

    if limit is None:
        return APIResponse.success(
            message="Blog posts retrieved successfully",
            data=posts_data,
        )
    pagination = create_pagination_meta(result.total, result.page, result.limit)
    return APIResponse.success(
        message="Blog posts retrieved successfully",
        data=posts_data,
        pagination=pagination,
    )


@router.get("/{post_id}")
async def get_blog_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a single blog post by ID
    """
    service = BlogPostService(db)
    post = await service.get_blog_post_by_id(post_id)
    
    if not post:
        return APIResponse.error(
            message="Blog post not found",
            status=status.HTTP_404_NOT_FOUND
        )
    
    post_data = BlogPostResponse.from_orm(post).model_dump()
    
    return APIResponse.success(
        message="Blog post retrieved successfully",
        data=post_data
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_blog_post(
    post_data: BlogPostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new blog post
    """
    service = BlogPostService(db)
    post = await service.create_blog_post(post_data)
    
    post_response = BlogPostResponse.from_orm(post).model_dump()
    
    return APIResponse.success(
        message="Blog post created successfully",
        status=status.HTTP_201_CREATED,
        data=post_response
    )


@router.put("/{post_id}")
async def update_blog_post(
    post_id: int,
    post_data: BlogPostUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a blog post
    """
    service = BlogPostService(db)
    post = await service.update_blog_post(post_id, post_data)
    
    post_response = BlogPostResponse.from_orm(post).model_dump()
    
    return APIResponse.success(
        message="Blog post updated successfully",
        data=post_response
    )


@router.delete("/{post_id}")
async def delete_blog_post(
    post_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a blog post
    """
    service = BlogPostService(db)
    await service.delete_blog_post(post_id)
    
    return APIResponse.success(
        message="Blog post deleted successfully"
    )
