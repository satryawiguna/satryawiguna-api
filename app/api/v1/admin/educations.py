"""
Admin Education API endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.schemas.education import EducationCreate, EducationUpdate, EducationResponse
from app.services.education_service import EducationService
from app.utils.response import APIResponse, create_pagination_meta
from app.api.dependencies import get_current_user
from app.models.user import User


router = APIRouter()


# ---------------------------------------------------------------------------
# Swagger response example data
# ---------------------------------------------------------------------------
_EDUCATION_DATA = {
    "id": 1,
    "degree": "Bachelor of Electrical Engineering",
    "institution": "Udayana University",
    "start_year": 2001,
    "end_year": 2006,
    "sort_order": 0,
    "created_at": "2026-05-30T00:00:00",
    "updated_at": "2026-05-30T00:00:00",
}

EDUCATIONS_LIST_EXAMPLES = {
    "with_pagination": {
        "summary": "With pagination (when limit is provided)",
        "description": "Response includes pagination metadata",
        "value": {
            "success": True,
            "status": 200,
            "message": "Educations retrieved successfully",
            "data": [_EDUCATION_DATA],
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
            "message": "Educations retrieved successfully",
            "data": [_EDUCATION_DATA],
            "timestamp": "2026-05-30T00:00:00.000Z",
        },
    },
}

EDUCATION_DETAIL_EXAMPLE = {
    "example": {
        "value": {
            "success": True,
            "status": 200,
            "message": "Education retrieved successfully",
            "data": _EDUCATION_DATA,
            "timestamp": "2026-05-30T00:00:00.000Z",
        }
    }
}



# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get(
    "",
    summary="Get all educations",
    description="""Get all educations with optional pagination and filters.

**Pagination Options:**
- With pagination: Provide `limit` parameter (default: 10)
- Without pagination: Set `limit` to `null` to get all educations

**Filters:**
- `keyword`: Search in degree or institution name
- `sortBy`: Field to sort by (default: sort_order)
- `sortOrder`: ASC or DESC (default: ASC)
""",
    responses={
        200: {
            "description": "Educations retrieved successfully",
            "content": {"application/json": {"examples": EDUCATIONS_LIST_EXAMPLES}},
        }
    },
)
async def get_educations(
    page: int = Query(1, ge=1, description="Page number"),
    limit: Optional[int] = Query(10, ge=1, le=100, description="Items per page. Set to null for all educations"),
    sortBy: str = Query("sort_order", description="Sort field"),
    sortOrder: str = Query("ASC", description="Sort order (ASC or DESC)"),
    keyword: Optional[str] = Query(None, description="Search keyword for degree or institution"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = EducationService(db)
    result = await service.get_educations(
        page=page,
        limit=limit,
        sort_by=sortBy,
        sort_order=sortOrder,
        keyword=keyword,
    )
    educations_data = [EducationResponse.from_orm(e).model_dump() for e in result.items]
    if limit is None:
        return APIResponse.success(message="Educations retrieved successfully", data=educations_data)
    pagination = create_pagination_meta(result.total, result.page, result.limit)
    return APIResponse.success(
        message="Educations retrieved successfully",
        data=educations_data,
        pagination=pagination,
    )


@router.post("", status_code=status.HTTP_201_CREATED, summary="Create education")
async def create_education(
    education_data: EducationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = EducationService(db)
    education = await service.create_education(education_data)
    return APIResponse.success(
        message="Education created successfully",
        status=status.HTTP_201_CREATED,
        data=EducationResponse.from_orm(education).model_dump(),
    )


@router.get(
    "/{education_id}",
    summary="Get education by ID",
    responses={
        200: {
            "description": "Education retrieved successfully",
            "content": {"application/json": EDUCATION_DETAIL_EXAMPLE},
        }
    },
)
async def get_education(
    education_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = EducationService(db)
    education = await service.get_education_by_id(education_id)
    if not education:
        return APIResponse.error(message="Education not found", status=status.HTTP_404_NOT_FOUND)
    return APIResponse.success(
        message="Education retrieved successfully",
        data=EducationResponse.from_orm(education).model_dump(),
    )


@router.put("/{education_id}", summary="Update education")
async def update_education(
    education_id: int,
    education_data: EducationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = EducationService(db)
    try:
        education = await service.update_education(education_id, education_data)
    except NotFoundError:
        return APIResponse.error(message="Education not found", status=status.HTTP_404_NOT_FOUND)
    return APIResponse.success(
        message="Education updated successfully",
        data=EducationResponse.from_orm(education).model_dump(),
    )


@router.delete("/{education_id}", summary="Delete education")
async def delete_education(
    education_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = EducationService(db)
    deleted = await service.delete_education(education_id)
    if not deleted:
        return APIResponse.error(message="Education not found", status=status.HTTP_404_NOT_FOUND)
    return APIResponse.success(message="Education deleted successfully")
