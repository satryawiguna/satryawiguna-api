"""
Public Projects API endpoints (read-only, no auth)
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.project import ProjectResponse
from app.services.project_service import ProjectService
from app.utils.response import APIResponse, create_pagination_meta


router = APIRouter()


@router.get("", summary="Get all projects (public)")
async def get_projects(
    page: int = Query(1, ge=1),
    limit: Optional[int] = Query(10, ge=1, le=100),
    sortBy: str = Query("created_at"),
    sortOrder: str = Query("DESC"),
    keyword: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)
    result = await service.get_projects(
        page=page, limit=limit, sort_by=sortBy, sort_order=sortOrder, keyword=keyword,
        published_only=True,
    )
    projects_data = [ProjectResponse.from_orm(p).model_dump() for p in result.items]
    if limit is None:
        return APIResponse.success(message="Projects retrieved successfully", data=projects_data)
    pagination = create_pagination_meta(result.total, result.page, result.limit)
    return APIResponse.success(message="Projects retrieved successfully", data=projects_data, pagination=pagination)


@router.get("/{project_id}", summary="Get a project by ID (public)")
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = ProjectService(db)
    project = await service.get_project_by_id(project_id, published_only=True)
    if not project:
        return APIResponse.error(message="Project not found", status=status.HTTP_404_NOT_FOUND)
    return APIResponse.success(message="Project retrieved successfully", data=ProjectResponse.from_orm(project).model_dump())

