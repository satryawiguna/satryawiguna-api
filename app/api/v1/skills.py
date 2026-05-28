"""
Skills API endpoints
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


router = APIRouter()


# Response examples for Swagger
SKILLS_LIST_EXAMPLES = {
    "with_pagination": {
        "summary": "With pagination (when limit is provided)",
        "description": "Response includes pagination metadata",
        "value": {
            "success": True,
            "status": 200,
            "message": "Skills retrieved successfully",
            "data": [
                {
                    "name": "Python",
                    "category_id": 1,
                    "level": 90,
                    "icon_url": "https://example.com/icons/python.svg",
                    "sort_order": 1,
                    "id": 1,
                    "category": {"id": 1, "name": "Backend", "slug": "backend", "type": "SKILL"}
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
            "data": [
                {
                    "name": "Python",
                    "category_id": 1,
                    "level": 90,
                    "icon_url": "https://example.com/icons/python.svg",
                    "sort_order": 1,
                    "id": 1,
                    "category": {"id": 1, "name": "Backend", "slug": "backend", "type": "SKILL"}
                }
            ],
            "timestamp": "2026-03-16T00:00:00.000Z"
        }
    }
}


@router.get(
    "",
    summary="Get all skills",
    description="""Get all skills with optional pagination and filters.

    **Pagination Options:**
    - With pagination: Provide `limit` parameter (default: 10)
    - Without pagination: Set `limit` to `null` to get all skills

    **Filters:**
    - `keyword`: Search in name
    - `category`: Filter by category ID
    - `sortBy`: Field to sort by (default: sort_order)
    - `sortOrder`: ASC or DESC (default: ASC)
    """,
    responses={
        200: {
            "description": "Skills retrieved successfully",
            "content": {
                "application/json": {
                    "examples": SKILLS_LIST_EXAMPLES
                }
            }
        }
    }
)
async def get_skills(
    page: int = Query(1, ge=1, description="Page number (only used when limit is provided)"),
    limit: Optional[int] = Query(10, ge=1, le=100, description="Items per page. Set to null for all skills without pagination"),
    sortBy: str = Query("sort_order", description="Sort field"),
    sortOrder: str = Query("ASC", description="Sort order (ASC or DESC)"),
    keyword: Optional[str] = Query(None, description="Search keyword for name"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all skills with optional pagination and filters.

    Returns list of skills with or without pagination based on limit parameter.
    """
    service = SkillService(db)
    result = await service.get_skills(
        page=page,
        limit=limit,
        sort_by=sortBy,
        sort_order=sortOrder,
        keyword=keyword,
        category_id=category_id,
    )

    skills_data = [SkillResponse.from_orm(skill).model_dump() for skill in result.items]

    if limit is None:
        return APIResponse.success(
            message="Skills retrieved successfully",
            data=skills_data,
        )
    pagination = create_pagination_meta(result.total, result.page, result.limit)
    return APIResponse.success(
        message="Skills retrieved successfully",
        data=skills_data,
        pagination=pagination,
    )


@router.get("/{skill_id}", summary="Get a skill by ID")
async def get_skill(
    skill_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a single skill by ID.
    """
    service = SkillService(db)
    skill = await service.get_skill_by_id(skill_id)

    if not skill:
        return APIResponse.error(
            message="Skill not found",
            status=status.HTTP_404_NOT_FOUND
        )

    return APIResponse.success(
        message="Skill retrieved successfully",
        data=SkillResponse.from_orm(skill).model_dump()
    )


@router.post("", status_code=status.HTTP_201_CREATED, summary="Create a new skill")
async def create_skill(
    skill_data: SkillCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new skill. Requires authentication.
    """
    service = SkillService(db)
    skill = await service.create_skill(skill_data)

    return APIResponse.success(
        message="Skill created successfully",
        status=status.HTTP_201_CREATED,
        data=SkillResponse.from_orm(skill).model_dump()
    )


@router.put("/{skill_id}", summary="Update a skill")
async def update_skill(
    skill_id: int,
    skill_data: SkillUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update an existing skill by ID. Requires authentication.
    """
    service = SkillService(db)
    skill = await service.update_skill(skill_id, skill_data)

    return APIResponse.success(
        message="Skill updated successfully",
        data=SkillResponse.from_orm(skill).model_dump()
    )


@router.delete("/{skill_id}", summary="Delete a skill")
async def delete_skill(
    skill_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a skill by ID. Requires authentication.
    """
    service = SkillService(db)
    await service.delete_skill(skill_id)

    return APIResponse.success(
        message="Skill deleted successfully"
    )
