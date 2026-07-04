"""
Admin Strength API endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.schemas.strength import StrengthCreate, StrengthUpdate, StrengthResponse
from app.services.strength_service import StrengthService
from app.utils.response import APIResponse, create_pagination_meta
from app.api.dependencies import get_current_user
from app.models.user import User


router = APIRouter()


# ---------------------------------------------------------------------------
# Swagger response example data
# ---------------------------------------------------------------------------
_STRENGTH_DATA = {
    "id": 1,
    "description": "System Architecture & Scalability",
    "sort_order": 0,
    "created_at": "2026-07-04T00:00:00",
    "updated_at": "2026-07-04T00:00:00",
}

STRENGTHS_LIST_EXAMPLES = {
    "with_pagination": {
        "summary": "With pagination (when limit is provided)",
        "description": "Response includes pagination metadata",
        "value": {
            "success": True,
            "status": 200,
            "message": "Strengths retrieved successfully",
            "data": [_STRENGTH_DATA],
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
            "message": "Strengths retrieved successfully",
            "data": [_STRENGTH_DATA],
            "timestamp": "2026-07-04T00:00:00.000Z",
        },
    },
}

STRENGTH_DETAIL_EXAMPLE = {
    "example": {
        "value": {
            "success": True,
            "status": 200,
            "message": "Strength retrieved successfully",
            "data": _STRENGTH_DATA,
            "timestamp": "2026-07-04T00:00:00.000Z",
        }
    }
}

STRENGTH_CREATE_EXAMPLE = {
    "example": {
        "value": {
            "success": True,
            "status": 201,
            "message": "Strength created successfully",
            "data": _STRENGTH_DATA,
            "timestamp": "2026-07-04T00:00:00.000Z",
        }
    }
}

STRENGTH_UPDATE_EXAMPLE = {
    "example": {
        "value": {
            "success": True,
            "status": 200,
            "message": "Strength updated successfully",
            "data": _STRENGTH_DATA,
            "timestamp": "2026-07-04T00:00:00.000Z",
        }
    }
}

STRENGTH_DELETE_EXAMPLE = {
    "example": {
        "value": {
            "success": True,
            "status": 200,
            "message": "Strength deleted successfully",
            "timestamp": "2026-07-04T00:00:00.000Z",
        }
    }
}


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.get(
    "",
    summary="Get all strengths",
    description="""Get all strengths with optional pagination and filters.

**Pagination Options:**
- With pagination: Provide `limit` parameter (default: 10)
- Without pagination: Set `limit` to `null` to get all strengths

**Filters:**
- `keyword`: Search in description
- `sortBy`: Field to sort by (default: sort_order)
- `sortOrder`: ASC or DESC (default: ASC)
""",
    responses={
        200: {
            "description": "Strengths retrieved successfully",
            "content": {"application/json": {"examples": STRENGTHS_LIST_EXAMPLES}},
        }
    },
)
async def get_strengths(
    page: int = Query(1, ge=1, description="Page number"),
    limit: Optional[int] = Query(10, ge=1, le=100, description="Items per page. Set to null for all strengths"),
    sortBy: str = Query("sort_order", description="Sort field"),
    sortOrder: str = Query("ASC", description="Sort order (ASC or DESC)"),
    keyword: Optional[str] = Query(None, description="Search keyword for description"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = StrengthService(db)
    result = await service.get_strengths(
        page=page,
        limit=limit,
        sort_by=sortBy,
        sort_order=sortOrder,
        keyword=keyword,
    )
    strengths_data = [StrengthResponse.from_orm(s).model_dump() for s in result.items]
    if limit is None:
        return APIResponse.success(message="Strengths retrieved successfully", data=strengths_data)
    pagination = create_pagination_meta(result.total, result.page, result.limit)
    return APIResponse.success(
        message="Strengths retrieved successfully",
        data=strengths_data,
        pagination=pagination,
    )


@router.post(
    "",
    summary="Create strength",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "Strength created successfully",
            "content": {"application/json": STRENGTH_CREATE_EXAMPLE},
        }
    },
)
async def create_strength(
    strength_data: StrengthCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = StrengthService(db)
    strength = await service.create_strength(strength_data)
    return APIResponse.success(
        message="Strength created successfully",
        status=status.HTTP_201_CREATED,
        data=StrengthResponse.from_orm(strength).model_dump(),
    )


@router.get(
    "/{strength_id}",
    summary="Get strength by ID",
    responses={
        200: {
            "description": "Strength retrieved successfully",
            "content": {"application/json": STRENGTH_DETAIL_EXAMPLE},
        }
    },
)
async def get_strength(
    strength_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = StrengthService(db)
    strength = await service.get_strength_by_id(strength_id)
    if not strength:
        return APIResponse.error(message="Strength not found", status=status.HTTP_404_NOT_FOUND)
    return APIResponse.success(
        message="Strength retrieved successfully",
        data=StrengthResponse.from_orm(strength).model_dump(),
    )


@router.put(
    "/{strength_id}",
    summary="Update strength",
    responses={
        200: {
            "description": "Strength updated successfully",
            "content": {"application/json": STRENGTH_UPDATE_EXAMPLE},
        }
    },
)
async def update_strength(
    strength_id: int,
    strength_data: StrengthUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = StrengthService(db)
    try:
        strength = await service.update_strength(strength_id, strength_data)
    except NotFoundError:
        return APIResponse.error(message="Strength not found", status=status.HTTP_404_NOT_FOUND)
    return APIResponse.success(
        message="Strength updated successfully",
        data=StrengthResponse.from_orm(strength).model_dump(),
    )


@router.delete(
    "/{strength_id}",
    summary="Delete strength",
    responses={
        200: {
            "description": "Strength deleted successfully",
            "content": {"application/json": STRENGTH_DELETE_EXAMPLE},
        }
    },
)
async def delete_strength(
    strength_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = StrengthService(db)
    deleted = await service.delete_strength(strength_id)
    if not deleted:
        return APIResponse.error(message="Strength not found", status=status.HTTP_404_NOT_FOUND)
    return APIResponse.success(message="Strength deleted successfully")
