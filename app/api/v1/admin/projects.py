"""
Admin Project API endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.services.project_service import ProjectService
from app.utils.response import APIResponse, create_pagination_meta
from app.api.dependencies import get_current_user
from app.models.user import User


router = APIRouter()


# Response examples for Swagger
PROJECTS_LIST_EXAMPLES = {
    "with_pagination": {
        "summary": "With pagination (when limit is provided)",
        "description": "Response includes pagination metadata",
        "value": {
            "success": True,
            "status": 200,
            "message": "Projects retrieved successfully",
            "data": [
                {
                    "id": 1,
                    "title": "E-Commerce Platform",
                    "sub_title": "A full-stack solution",
                    "slug": "ecommerce-platform",
                    "description": "Full-featured e-commerce solution",
                    "content": "Built with FastAPI and React...",
                    "demo_url": "https://demo.example.com",
                    "repository_url": "https://github.com/example/project",
                    "thumbnail_url": "https://example.com/thumb.jpg",
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
            "message": "Projects retrieved successfully",
            "data": [
                {
                    "id": 1,
                    "title": "E-Commerce Platform",
                    "sub_title": "A full-stack solution",
                    "slug": "ecommerce-platform",
                    "description": "Full-featured e-commerce solution",
                    "content": "Built with FastAPI and React...",
                    "demo_url": "https://demo.example.com",
                    "repository_url": "https://github.com/example/project",
                    "thumbnail_url": "https://example.com/thumb.jpg",
                    "published_at": "2026-03-15T00:00:00",
                    "created_at": "2026-03-15T22:22:19",
                    "updated_at": "2026-03-15T22:22:19"
                }
            ],
            "timestamp": "2026-03-16T02:28:18.642Z"
        }
    }
}


@router.get(
    "",
    summary="Get all projects",
    description="""Get all projects with optional pagination and filters.
    
    **Pagination Options:**
    - With pagination: Provide `limit` parameter (default: 10)
    - Without pagination: Set `limit` to `null` to get all projects
    
    **Filters:**
    - `keyword`: Search in title or description
    - `category_id`: Filter by category ID
    - `skill_id`: Filter by skill ID
    - `sortBy`: Field to sort by (default: created_at)
    - `sortOrder`: ASC or DESC (default: DESC)
    """,
    responses={
        200: {
            "description": "Projects retrieved successfully",
            "content": {
                "application/json": {
                    "examples": PROJECTS_LIST_EXAMPLES
                }
            }
        }
    }
)
async def get_projects(
    page: int = Query(1, ge=1, description="Page number (only used when limit is provided)"),
    limit: Optional[int] = Query(10, ge=1, le=100, description="Items per page. Set to null for all projects without pagination"),
    sortBy: str = Query("created_at", description="Sort field"),
    sortOrder: str = Query("DESC", description="Sort order (ASC or DESC)"),
    keyword: Optional[str] = Query(None, description="Search keyword for title or description"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    skill_id: Optional[int] = Query(None, description="Filter by skill ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ProjectService(db)
    result = await service.get_projects(
        page=page,
        limit=limit,
        sort_by=sortBy,
        sort_order=sortOrder,
        keyword=keyword,
        category_id=category_id,
        skill_id=skill_id,
    )

    projects_data = [ProjectResponse.from_orm(project).model_dump() for project in result.items]

    if limit is None:
        return APIResponse.success(
            message="Projects retrieved successfully",
            data=projects_data,
        )
    pagination = create_pagination_meta(result.total, result.page, result.limit)
    return APIResponse.success(
        message="Projects retrieved successfully",
        data=projects_data,
        pagination=pagination,
    )


PROJECT_DETAIL_EXAMPLE = {
    "example": {
        "value": {
            "success": True,
            "status": 200,
            "message": "Project retrieved successfully",
            "data": {
                "id": 1,
                "title": "E-Commerce Platform",
                "sub_title": "Shopping platform for everyone",
                "slug": "ecommerce-platform",
                "description": "Full-featured e-commerce solution",
                "content": "Built with FastAPI and React...",
                "demo_url": "https://demo.example.com",
                "repository_url": "https://github.com/example/project",
                "thumbnail_url": "https://example.com/thumb.jpg",
                "published_at": "2026-03-15T00:00:00",
                "created_at": "2026-03-15T22:22:19",
                "updated_at": "2026-03-15T22:22:19",
                "skills": [
                    {"id": 1, "name": "Python", "icon_url": "https://example.com/py.svg"}
                ],
                "images": [
                    {"id": 1, "image_url": "https://example.com/img.jpg"}
                ],
                "categories": [
                    {"id": 1, "name": "Web", "slug": "web"}
                ]
            },
            "timestamp": "2026-03-15T23:20:01.545Z"
        }
    }
}


@router.get(
    "/{project_id}",
    summary="Get Project",
    description="Get a single project by ID",
    responses={
        200: {
            "description": "Project retrieved successfully",
            "content": {
                "application/json": {
                    "examples": PROJECT_DETAIL_EXAMPLE
                }
            }
        }
    }
)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a single project by ID
    """
    service = ProjectService(db)
    project = await service.get_project_by_id(project_id)
    
    if not project:
        return APIResponse.error(
            message="Project not found",
            status=status.HTTP_404_NOT_FOUND
        )
    
    project_data = ProjectResponse.from_orm(project).model_dump()
    
    return APIResponse.success(
        message="Project retrieved successfully",
        data=project_data
    )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create Project",
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "example": {
                        "title": "E-Commerce Platform",
                        "sub_title": "Shopping platform for everyone",
                        "slug": "ecommerce-platform",
                        "description": "Full-featured e-commerce solution",
                        "content": "Built with FastAPI and React...",
                        "demo_url": "https://demo.example.com",
                        "repository_url": "https://github.com/example/project",
                        "thumbnail_url": "https://example.com/thumb.jpg",
                        "skill_ids": [1, 2],
                        "image_urls": ["https://example.com/img1.jpg", "https://example.com/img2.jpg"],
                        "category_ids": [1]
                    }
                }
            }
        }
    }
)
async def create_project(
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new project
    """
    service = ProjectService(db)
    project = await service.create_project(project_data)
    
    project_response = ProjectResponse.from_orm(project).model_dump()
    
    return APIResponse.success(
        message="Project created successfully",
        status=status.HTTP_201_CREATED,
        data=project_response
    )


@router.put("/{project_id}")
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a project
    """
    service = ProjectService(db)
    project = await service.update_project(project_id, project_data)
    
    project_response = ProjectResponse.from_orm(project).model_dump()
    
    return APIResponse.success(
        message="Project updated successfully",
        data=project_response
    )


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a project
    """
    service = ProjectService(db)
    await service.delete_project(project_id)
    
    return APIResponse.success(
        message="Project deleted successfully"
    )
