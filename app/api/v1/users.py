"""
User API endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services.user_service import UserService
from app.utils.response import APIResponse, create_pagination_meta
from app.api.dependencies import get_current_user
from app.models.user import User


router = APIRouter()


# Response examples for Swagger
USERS_LIST_EXAMPLES = {
    "with_pagination": {
        "summary": "With pagination (when limit is provided)",
        "description": "Response includes pagination metadata",
        "value": {
            "success": True,
            "status": 200,
            "message": "Users retrieved successfully",
            "data": [
                {
                    "name": "Admin User",
                    "email": "admin@satryawiguna.me",
                    "id": 1,
                    "email_verified_at": None,
                    "created_at": "2026-03-15T22:22:19",
                    "updated_at": "2026-03-15T22:22:19"
                },
                {
                    "name": "John Doe",
                    "email": "john@example.com",
                    "id": 2,
                    "email_verified_at": None,
                    "created_at": "2026-03-15T22:22:19",
                    "updated_at": "2026-03-15T22:22:19"
                },
                {
                    "name": "Jane Smith",
                    "email": "jane@example.com",
                    "id": 3,
                    "email_verified_at": None,
                    "created_at": "2026-03-15T22:22:19",
                    "updated_at": "2026-03-15T22:22:19"
                }
            ],
            "pagination": {
                "total": 3,
                "page": 1,
                "limit": 10,
                "totalPages": 1,
                "hasNextPage": False,
                "hasPreviousPage": False
            },
            "timestamp": "2026-03-15T23:20:01.545Z"
        }
    },
    "without_pagination": {
        "summary": "Without pagination (when limit is omitted)",
        "description": "Response without pagination metadata",
        "value": {
            "success": True,
            "status": 200,
            "message": "Users retrieved successfully",
            "data": [
                {
                    "name": "Admin User",
                    "email": "admin@satryawiguna.me",
                    "id": 1,
                    "email_verified_at": None,
                    "created_at": "2026-03-15T22:22:19",
                    "updated_at": "2026-03-15T22:22:19"
                },
                {
                    "name": "John Doe",
                    "email": "john@example.com",
                    "id": 2,
                    "email_verified_at": None,
                    "created_at": "2026-03-15T22:22:19",
                    "updated_at": "2026-03-15T22:22:19"
                },
                {
                    "name": "Jane Smith",
                    "email": "jane@example.com",
                    "id": 3,
                    "email_verified_at": None,
                    "created_at": "2026-03-15T22:22:19",
                    "updated_at": "2026-03-15T22:22:19"
                }
            ],
            "timestamp": "2026-03-15T23:20:01.545Z"
        }
    }
}


USER_SINGLE_EXAMPLE = {
    "success": True,
    "status": 200,
    "message": "User retrieved successfully",
    "data": {
        "name": "Admin User",
        "email": "admin@satryawiguna.me",
        "id": 1,
        "email_verified_at": None,
        "created_at": "2026-03-15T22:22:19",
        "updated_at": "2026-03-15T22:22:19"
    },
    "timestamp": "2026-03-15T23:20:01.545Z"
}


router = APIRouter()


@router.get(
    "",
    summary="Get all users",
    description="""Get all users with optional pagination and filters.
    
    **Pagination Options:**
    - With pagination: Provide `limit` parameter (default: 10)
    - Without pagination: Set `limit` to `null` to get all users
    
    **Filters:**
    - `keyword`: Search in name or email
    - `sortBy`: Field to sort by (default: created_at)
    - `sortOrder`: ASC or DESC (default: DESC)
    """,
    responses={
        200: {
            "description": "Users retrieved successfully",
            "content": {
                "application/json": {
                    "examples": USERS_LIST_EXAMPLES
                }
            }
        }
    }
)
async def get_users(
    page: int = Query(1, ge=1, description="Page number (only used when limit is provided)"),
    limit: Optional[int] = Query(10, ge=1, le=100, description="Items per page. Set to null for all users without pagination"),
    sortBy: str = Query("created_at", description="Sort field"),
    sortOrder: str = Query("DESC", description="Sort order (ASC or DESC)"),
    keyword: Optional[str] = Query(None, description="Search keyword for name or email"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all users with optional pagination and filters.
    
    Returns list of users with or without pagination based on limit parameter.
    """
    service = UserService(db)
    result = await service.get_users(
        page=page,
        limit=limit,
        sort_by=sortBy,
        sort_order=sortOrder,
        keyword=keyword,
    )

    users_data = [UserResponse.from_orm(user).model_dump() for user in result.items]

    if limit is None:
        return APIResponse.success(
            message="Users retrieved successfully",
            data=users_data,
        )
    pagination = create_pagination_meta(result.total, result.page, result.limit)
    return APIResponse.success(
        message="Users retrieved successfully",
        data=users_data,
        pagination=pagination,
    )


@router.get(
    "/{user_id}",
    summary="Get user by ID",
    responses={
        200: {
            "description": "User retrieved successfully",
            "content": {
                "application/json": {
                    "example": USER_SINGLE_EXAMPLE
                }
            }
        }
    }
)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a single user by ID
    """
    service = UserService(db)
    user = await service.get_user_by_id(user_id)
    
    if not user:
        return APIResponse.error(
            message="User not found",
            status=status.HTTP_404_NOT_FOUND
        )
    
    user_data = UserResponse.from_orm(user).model_dump()
    
    return APIResponse.success(
        message="User retrieved successfully",
        data=user_data
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new user
    """
    service = UserService(db)
    user = await service.create_user(user_data)

    user_data = UserResponse.from_orm(user).model_dump()
    
    return APIResponse.success(
        message="User created successfully",
        status=status.HTTP_201_CREATED,
        data=user_data
    )


@router.put("/{user_id}")
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a user
    """
    service = UserService(db)
    user = await service.update_user(user_id, user_data)
    
    user_response = UserResponse.from_orm(user).model_dump()
    
    return APIResponse.success(
        message="User updated successfully",
        data=user_response
    )


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a user
    """
    service = UserService(db)
    await service.delete_user(user_id)
    
    return APIResponse.success(
        message="User deleted successfully"
    )
