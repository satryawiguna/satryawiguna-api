"""
Admin Career Impact API endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.schemas.career_impact import CareerImpactCreate, CareerImpactUpdate, CareerImpactResponse
from app.services.career_impact_service import CareerImpactService
from app.utils.response import APIResponse, create_pagination_meta
from app.api.dependencies import get_current_user
from app.models.user import User


router = APIRouter()


# ---------------------------------------------------------------------------
# Swagger response example data
# ---------------------------------------------------------------------------
_CAREER_IMPACT_DATA = {
    "id": 1,
    "title": "Regional Full-Stack Role",
    "description": "Built cross-border event management systems for HK, MY, SG, PH, and ID with ReactJS and .NET Core backends.",
    "quote": "Scaling platforms for 500k+ daily active users",
    "icon_url": "https://cdn.satryawiguna.me/icons/globe.svg",
    "sort_order": 0,
    "created_at": "2026-07-04T00:00:00",
    "updated_at": "2026-07-04T00:00:00",
}

CAREER_IMPACTS_LIST_EXAMPLES = {
    "with_pagination": {
        "summary": "With pagination (when limit is provided)",
        "description": "Response includes pagination metadata",
        "value": {
            "success": True,
            "status": 200,
            "message": "Career impacts retrieved successfully",
            "data": [_CAREER_IMPACT_DATA],
            "pagination": {
                "total": 1,
                "page": 1,
                "limit": 10,
                "totalPages": 1,
                "hasNextPage": False,
                "hasPreviousPage": False,
            },
            "timestamp": "2026-07-04T00:00:00.000Z",
        },
    },
    "without_pagination": {
        "summary": "Without pagination (when limit is omitted)",
        "description": "Response without pagination metadata",
        "value": {
            "success": True,
            "status": 200,
            "message": "Career impacts retrieved successfully",
            "data": [_CAREER_IMPACT_DATA],
            "timestamp": "2026-07-04T00:00:00.000Z",
        },
    },
}

CAREER_IMPACT_DETAIL_EXAMPLE = {
    "example": {
        "value": {
            "success": True,
            "status": 200,
            "message": "Career impact retrieved successfully",
            "data": _CAREER_IMPACT_DATA,
            "timestamp": "2026-07-04T00:00:00.000Z",
        }
    }
}

CAREER_IMPACT_CREATE_EXAMPLE = {
    "example": {
        "value": {
            "success": True,
            "status": 201,
            "message": "Career impact created successfully",
            "data": _CAREER_IMPACT_DATA,
            "timestamp": "2026-07-04T00:00:00.000Z",
        }
    }
}

CAREER_IMPACT_UPDATE_EXAMPLE = {
    "example": {
        "value": {
            "success": True,
            "status": 200,
            "message": "Career impact updated successfully",
            "data": _CAREER_IMPACT_DATA,
            "timestamp": "2026-07-04T00:00:00.000Z",
        }
    }
}

CAREER_IMPACT_DELETE_EXAMPLE = {
    "example": {
        "value": {
            "success": True,
            "status": 200,
            "message": "Career impact deleted successfully",
            "timestamp": "2026-07-04T00:00:00.000Z",
        }
    }
}


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.get(
    "",
    summary="Get all career impacts",
    description="""Get all career impacts with optional pagination and filters.

**Pagination Options:**
- With pagination: Provide `limit` parameter (default: 10)
- Without pagination: Set `limit` to `null` to get all career impacts

**Filters:**
- `keyword`: Search in title
- `sortBy`: Field to sort by (default: sort_order)
- `sortOrder`: ASC or DESC (default: ASC)
""",
    responses={
        200: {
            "description": "Career impacts retrieved successfully",
            "content": {"application/json": {"examples": CAREER_IMPACTS_LIST_EXAMPLES}},
        }
    },
)
async def get_career_impacts(
    page: int = Query(1, ge=1, description="Page number"),
    limit: Optional[int] = Query(10, ge=1, le=100, description="Items per page. Set to null for all career impacts"),
    sortBy: str = Query("sort_order", description="Sort field"),
    sortOrder: str = Query("ASC", description="Sort order (ASC or DESC)"),
    keyword: Optional[str] = Query(None, description="Search keyword for title"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CareerImpactService(db)
    result = await service.get_career_impacts(
        page=page,
        limit=limit,
        sort_by=sortBy,
        sort_order=sortOrder,
        keyword=keyword,
    )
    career_impacts_data = [CareerImpactResponse.from_orm(s).model_dump() for s in result.items]
    if limit is None:
        return APIResponse.success(message="Career impacts retrieved successfully", data=career_impacts_data)
    pagination = create_pagination_meta(result.total, result.page, result.limit)
    return APIResponse.success(
        message="Career impacts retrieved successfully",
        data=career_impacts_data,
        pagination=pagination,
    )


@router.post(
    "",
    summary="Create career impact",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "Career impact created successfully",
            "content": {"application/json": CAREER_IMPACT_CREATE_EXAMPLE},
        }
    },
)
async def create_career_impact(
    career_impact_data: CareerImpactCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CareerImpactService(db)
    career_impact = await service.create_career_impact(career_impact_data)
    return APIResponse.success(
        message="Career impact created successfully",
        status=status.HTTP_201_CREATED,
        data=CareerImpactResponse.from_orm(career_impact).model_dump(),
    )


@router.get(
    "/{career_impact_id}",
    summary="Get career impact by ID",
    responses={
        200: {
            "description": "Career impact retrieved successfully",
            "content": {"application/json": CAREER_IMPACT_DETAIL_EXAMPLE},
        }
    },
)
async def get_career_impact(
    career_impact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CareerImpactService(db)
    career_impact = await service.get_career_impact_by_id(career_impact_id)
    if not career_impact:
        return APIResponse.error(message="Career impact not found", status=status.HTTP_404_NOT_FOUND)
    return APIResponse.success(
        message="Career impact retrieved successfully",
        data=CareerImpactResponse.from_orm(career_impact).model_dump(),
    )


@router.put(
    "/{career_impact_id}",
    summary="Update career impact",
    responses={
        200: {
            "description": "Career impact updated successfully",
            "content": {"application/json": CAREER_IMPACT_UPDATE_EXAMPLE},
        }
    },
)
async def update_career_impact(
    career_impact_id: int,
    career_impact_data: CareerImpactUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CareerImpactService(db)
    try:
        career_impact = await service.update_career_impact(career_impact_id, career_impact_data)
    except NotFoundError:
        return APIResponse.error(message="Career impact not found", status=status.HTTP_404_NOT_FOUND)
    return APIResponse.success(
        message="Career impact updated successfully",
        data=CareerImpactResponse.from_orm(career_impact).model_dump(),
    )


@router.delete(
    "/{career_impact_id}",
    summary="Delete career impact",
    responses={
        200: {
            "description": "Career impact deleted successfully",
            "content": {"application/json": CAREER_IMPACT_DELETE_EXAMPLE},
        }
    },
)
async def delete_career_impact(
    career_impact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CareerImpactService(db)
    deleted = await service.delete_career_impact(career_impact_id)
    if not deleted:
        return APIResponse.error(message="Career impact not found", status=status.HTTP_404_NOT_FOUND)
    return APIResponse.success(message="Career impact deleted successfully")
