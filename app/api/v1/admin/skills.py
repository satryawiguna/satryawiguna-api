"""
Admin Skills API endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.other import SkillCreate, SkillUpdate, SkillResponse
from app.services.skill_service import SkillService
from app.utils.response import APIResponse, create_pagination_meta
from app.api.dependencies import get_current_user
from app.models.user import User


# Allowed level operators
LEVEL_OPERATORS = {"eq", "lt", "lte", "gt", "gte"}

router = APIRouter()

_SKILL_DATA = {
    "id": 1,
    "name": "Python",
    "category_id": 1,
    "level": 90,
    "icon_url": "https://example.com/icons/python.svg",
    "sort_order": 1,
    "category": {"id": 1, "name": "Backend", "slug": "backend", "type": "SKILL"}
}

SKILLS_LIST_EXAMPLES = {
    "with_pagination": {
        "summary": "With pagination (when limit is provided)",
        "description": "Response includes pagination metadata",
        "value": {
            "success": True,
            "status": 200,
            "message": "Skills retrieved successfully",
            "data": [_SKILL_DATA],
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
            "message": "Skills retrieved successfully",
            "data": [_SKILL_DATA],
            "timestamp": "2026-03-16T00:00:00.000Z"
        }
    },
    "level_filtered": {
        "summary": "Filtered by level (gte 80)",
        "description": "Response filtered by level >= 80 using level=80&level_operator=gte",
        "value": {
            "success": True,
            "status": 200,
            "message": "Skills retrieved successfully",
            "data": [_SKILL_DATA],
            "pagination": {
                "total": 1, "page": 1, "limit": 10,
                "totalPages": 1, "hasNextPage": False, "hasPreviousPage": False
            },
            "timestamp": "2026-03-16T00:00:00.000Z"
        }
    }
}


@router.get(
    "",
    summary="Get all skills",
    description="Get all skills with optional pagination, keyword, category filter, and dynamic level filter.",
    responses={
        200: {
            "description": "Skills retrieved successfully",
            "content": {"application/json": {"examples": SKILLS_LIST_EXAMPLES}}
        }
    }
)
async def get_skills(
    page: int = Query(1, ge=1),
    limit: Optional[int] = Query(10, ge=1, le=100),
    sortBy: str = Query("sort_order"),
    sortOrder: str = Query("ASC"),
    keyword: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    level: Optional[int] = Query(None, ge=0, le=100, description="Filter by level value. Use with level_operator to specify comparison type."),
    level_operator: str = Query("eq", description="Comparison operator for level filter. Allowed: eq, lt, lte, gt, gte"),
    db: AsyncSession = Depends(get_db),
):
    # Validate level_operator
    if level is not None and level_operator not in LEVEL_OPERATORS:
        return APIResponse.error(
            message=f"Invalid level_operator '{level_operator}'. Allowed values: {', '.join(sorted(LEVEL_OPERATORS))}",
            status=422,
        )

    service = SkillService(db)
    result = await service.get_skills(
        page=page, limit=limit, sort_by=sortBy, sort_order=sortOrder,
        keyword=keyword, category_id=category_id,
        level=level, level_operator=level_operator,
    )
    skills_data = [SkillResponse.from_orm(skill).model_dump() for skill in result.items]
    if limit is None:
        return APIResponse.success(message="Skills retrieved successfully", data=skills_data)
    pagination = create_pagination_meta(result.total, result.page, result.limit)
    return APIResponse.success(message="Skills retrieved successfully", data=skills_data, pagination=pagination)


@router.get(
    "/{skill_id}",
    summary="Get a skill by ID",
    responses={
        200: {
            "description": "Skill retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "status": 200,
                        "message": "Skill retrieved successfully",
                        "data": {
                            "id": 1,
                            "name": "Python",
                            "category_id": 1,
                            "level": 90,
                            "icon_url": "https://example.com/icons/python.svg",
                            "sort_order": 1,
                            "category": {"id": 1, "name": "Backend", "slug": "backend", "type": "SKILL"}
                        },
                        "timestamp": "2026-03-16T02:28:18.642Z"
                    }
                }
            }
        }
    }
)
async def get_skill(
    skill_id: int,
    db: AsyncSession = Depends(get_db),
):
    service = SkillService(db)
    skill = await service.get_skill_by_id(skill_id)
    if not skill:
        return APIResponse.error(message="Skill not found", status=status.HTTP_404_NOT_FOUND)
    return APIResponse.success(message="Skill retrieved successfully", data=SkillResponse.from_orm(skill).model_dump())


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create a skill",
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "example": {
                        "name": "Python",
                        "category_id": 1,
                        "level": 90,
                        "icon_url": "https://example.com/icons/python.svg",
                        "sort_order": 1
                    }
                }
            }
        }
    }
)
async def create_skill(
    skill_data: SkillCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = SkillService(db)
    skill = await service.create_skill(skill_data)
    return APIResponse.success(
        message="Skill created successfully",
        status=status.HTTP_201_CREATED,
        data=SkillResponse.from_orm(skill).model_dump()
    )


@router.put(
    "/{skill_id}",
    summary="Update a skill",
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "example": {
                        "name": "Python",
                        "category_id": 1,
                        "level": 95,
                        "icon_url": "https://example.com/icons/python.svg",
                        "sort_order": 1
                    }
                }
            }
        }
    }
)
async def update_skill(
    skill_id: int,
    skill_data: SkillUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = SkillService(db)
    skill = await service.update_skill(skill_id, skill_data)
    return APIResponse.success(message="Skill updated successfully", data=SkillResponse.from_orm(skill).model_dump())


@router.delete("/{skill_id}", summary="Delete a skill")
async def delete_skill(
    skill_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = SkillService(db)
    await service.delete_skill(skill_id)
    return APIResponse.success(message="Skill deleted successfully")
