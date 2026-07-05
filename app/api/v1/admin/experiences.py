"""
Admin Experience API endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.schemas.experience import ExperienceCreate, ExperienceUpdate, ExperienceResponse
from app.services.experience_service import ExperienceService
from app.utils.response import APIResponse, create_pagination_meta
from app.api.dependencies import get_current_user
from app.models.user import User


router = APIRouter()


# ---------------------------------------------------------------------------
# Swagger response example data
# ---------------------------------------------------------------------------
_EXPERIENCE_DATA = {
    "id": 1,
    "title": "Full Stack Developer",
    "company": "Explnc",
    "employment_type": "FULL_TIME",
    "description": "Built and scaled B2B and B2C platforms, improved user engagement and responsiveness.",
    "start_date": "2025-05-01",
    "end_date": None,
    "sort_order": 0,
    "created_at": "2026-05-30T00:00:00",
    "updated_at": "2026-05-30T00:00:00",
    "skills": [
        {"id": 1, "name": "Next.js", "icon_url": None},
        {"id": 2, "name": "Nest.js", "icon_url": None},
    ],
}

EXPERIENCES_LIST_EXAMPLES = {
    "with_pagination": {
        "summary": "With pagination (when limit is provided)",
        "description": "Response includes pagination metadata",
        "value": {
            "success": True,
            "status": 200,
            "message": "Experiences retrieved successfully",
            "data": [_EXPERIENCE_DATA],
            "pagination": {
                "total": 1,
                "page": 1,
                "limit": 10,
                "totalPages": 1,
                "hasNextPage": False,
                "hasPreviousPage": False,
            },
            "timestamp": "2026-05-30T00:00:00.000Z",
        },
    },
    "without_pagination": {
        "summary": "Without pagination (when limit is omitted)",
        "description": "Response without pagination metadata",
        "value": {
            "success": True,
            "status": 200,
            "message": "Experiences retrieved successfully",
            "data": [_EXPERIENCE_DATA],
            "timestamp": "2026-05-30T00:00:00.000Z",
        },
    },
}

EXPERIENCE_DETAIL_EXAMPLE = {
    "example": {
        "value": {
            "success": True,
            "status": 200,
            "message": "Experience retrieved successfully",
            "data": _EXPERIENCE_DATA,
            "timestamp": "2026-05-30T00:00:00.000Z",
        }
    }
}

EXPERIENCE_UPDATE_EXAMPLE = {
    "example": {
        "value": {
            "success": True,
            "status": 200,
            "message": "Experience updated successfully",
            "data": _EXPERIENCE_DATA,
            "timestamp": "2026-05-30T00:00:00.000Z",
        }
    }
}

EXPERIENCE_DELETE_EXAMPLE = {
    "example": {
        "value": {
            "success": True,
            "status": 200,
            "message": "Experience deleted successfully",
            "timestamp": "2026-05-30T00:00:00.000Z",
        }
    }
}


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get(
    "",
    summary="Get all experiences",
    description="""Get all experiences with optional pagination and filters.

**Pagination Options:**
- With pagination: Provide `limit` parameter (default: 10)
- Without pagination: Set `limit` to `null` to get all experiences

**Filters:**
- `keyword`: Search in title or company name
- `sortBy`: Field to sort by (default: sort_order)
- `sortOrder`: ASC or DESC (default: ASC)
""",
    responses={
        200: {
            "description": "Experiences retrieved successfully",
            "content": {"application/json": {"examples": EXPERIENCES_LIST_EXAMPLES}},
        }
    },
)
async def get_experiences(
    page: int = Query(1, ge=1, description="Page number"),
    limit: Optional[int] = Query(10, ge=1, le=100, description="Items per page. Set to null for all experiences"),
    sortBy: str = Query("sort_order", description="Sort field"),
    sortOrder: str = Query("ASC", description="Sort order (ASC or DESC)"),
    keyword: Optional[str] = Query(None, description="Search keyword for title or company"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ExperienceService(db)
    result = await service.get_experiences(
        page=page,
        limit=limit,
        sort_by=sortBy,
        sort_order=sortOrder,
        keyword=keyword,
    )
    experiences_data = [ExperienceResponse.from_orm(e).model_dump() for e in result.items]
    if limit is None:
        return APIResponse.success(message="Experiences retrieved successfully", data=experiences_data)
    pagination = create_pagination_meta(result.total, result.page, result.limit)
    return APIResponse.success(
        message="Experiences retrieved successfully",
        data=experiences_data,
        pagination=pagination,
    )


@router.post("", status_code=status.HTTP_201_CREATED, summary="Create experience")
async def create_experience(
    experience_data: ExperienceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ExperienceService(db)
    experience = await service.create_experience(experience_data)
    return APIResponse.success(
        message="Experience created successfully",
        status=status.HTTP_201_CREATED,
        data=ExperienceResponse.from_orm(experience).model_dump(),
    )


@router.get(
    "/{experience_id}",
    summary="Get experience by ID",
    responses={
        200: {
            "description": "Experience retrieved successfully",
            "content": {"application/json": EXPERIENCE_DETAIL_EXAMPLE},
        }
    },
)
async def get_experience(
    experience_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ExperienceService(db)
    experience = await service.get_experience_by_id(experience_id)
    if not experience:
        return APIResponse.error(message="Experience not found", status=status.HTTP_404_NOT_FOUND)
    return APIResponse.success(
        message="Experience retrieved successfully",
        data=ExperienceResponse.from_orm(experience).model_dump(),
    )


@router.put(
    "/{experience_id}",
    summary="Update experience",
    responses={
        200: {
            "description": "Experience updated successfully",
            "content": {"application/json": EXPERIENCE_UPDATE_EXAMPLE},
        }
    },
)
async def update_experience(
    experience_id: int,
    experience_data: ExperienceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ExperienceService(db)
    try:
        experience = await service.update_experience(experience_id, experience_data)
    except NotFoundError:
        return APIResponse.error(message="Experience not found", status=status.HTTP_404_NOT_FOUND)
    return APIResponse.success(
        message="Experience updated successfully",
        data=ExperienceResponse.from_orm(experience).model_dump(),
    )


@router.delete(
    "/{experience_id}",
    summary="Delete experience",
    responses={
        200: {
            "description": "Experience deleted successfully",
            "content": {"application/json": EXPERIENCE_DELETE_EXAMPLE},
        }
    },
)
async def delete_experience(
    experience_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ExperienceService(db)
    deleted = await service.delete_experience(experience_id)
    if not deleted:
        return APIResponse.error(message="Experience not found", status=status.HTTP_404_NOT_FOUND)
    return APIResponse.success(message="Experience deleted successfully")
