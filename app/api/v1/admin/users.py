"""
Admin User API endpoints
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
                    "phone": "+1234567890",
                    "avatar_url": "https://example.com/avatars/admin.jpg",
                    "id": 1,
                    "created_at": "2026-03-15T22:22:19",
                    "updated_at": "2026-03-15T22:22:19"
                },
                {
                    "name": "John Doe",
                    "email": "john@example.com",
                    "phone": "+9876543210",
                    "avatar_url": "https://example.com/avatars/john.jpg",
                    "id": 2,
                    "created_at": "2026-03-15T22:22:19",
                    "updated_at": "2026-03-15T22:22:19"
                },
                {
                    "name": "Jane Smith",
                    "email": "jane@example.com",
                    "phone": "+1122334455",
                    "avatar_url": "https://example.com/avatars/jane.jpg",
                    "id": 3,
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
                    "phone": "+1234567890",
                    "avatar_url": "https://example.com/avatars/admin.jpg",
                    "id": 1,
                    "created_at": "2026-03-15T22:22:19",
                    "updated_at": "2026-03-15T22:22:19"
                },
                {
                    "name": "John Doe",
                    "email": "john@example.com",
                    "phone": "+9876543210",
                    "avatar_url": "https://example.com/avatars/john.jpg",
                    "id": 2,
                    "created_at": "2026-03-15T22:22:19",
                    "updated_at": "2026-03-15T22:22:19"
                },
                {
                    "name": "Jane Smith",
                    "email": "jane@example.com",
                    "phone": "+1122334455",
                    "avatar_url": "https://example.com/avatars/jane.jpg",
                    "id": 3,
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
        "phone": "+1234567890",
        "avatar_url": "https://example.com/avatars/admin.jpg",
        "id": 1,
        "created_at": "2026-03-15T22:22:19",
        "updated_at": "2026-03-15T22:22:19"
    },
    "timestamp": "2026-03-15T23:20:01.545Z"
}

USER_CREATED_EXAMPLE = {
    "summary": "User created successfully",
    "value": {
        "success": True,
        "status": 201,
        "message": "User created successfully",
        "data": {
            "name": "New User",
            "email": "newuser@example.com",
            "phone": "+1234567890",
            "avatar_url": "https://example.com/avatars/newuser.jpg",
            "id": 4,
            "created_at": "2026-05-15T10:30:00.000Z",
            "updated_at": "2026-05-15T10:30:00.000Z"
        },
        "timestamp": "2026-05-15T10:30:00.000Z"
    }
}

USER_UPDATED_EXAMPLE = {
    "summary": "User updated successfully",
    "value": {
        "success": True,
        "status": 200,
        "message": "User updated successfully",
        "data": {
            "name": "Updated Name",
            "email": "updated@example.com",
            "phone": "+1234567890",
            "avatar_url": "https://example.com/avatar.jpg",
            "id": 2,
            "created_at": "2026-03-15T22:22:19",
            "updated_at": "2026-05-15T10:30:00.000Z"
        },
        "timestamp": "2026-05-15T10:30:00.000Z"
    }
}

USER_DELETED_EXAMPLE = {
    "summary": "User deleted successfully",
    "value": {
        "success": True,
        "status": 200,
        "message": "User deleted successfully",
        "timestamp": "2026-05-15T10:30:00.000Z"
    }
}


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
        },
        404: {"description": "User not found"},
        401: {"description": "Authentication required"},
    },
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


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="""Create a new user with name, email, and password.

The password will be hashed before storage. The response includes the
full user object with `phone` and `avatar_url` fields (both nullable).

Requires authentication.
""",
    responses={
        201: {
            "description": "User created successfully",
            "content": {
                "application/json": {
                    "examples": {"success": USER_CREATED_EXAMPLE}
                }
            }
        },
        400: {"description": "Duplicate email or validation error"},
        401: {"description": "Authentication required"},
    },
)
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

    user_response = UserResponse.from_orm(user).model_dump()
    
    return APIResponse.success(
        message="User created successfully",
        status=status.HTTP_201_CREATED,
        data=user_response
    )


@router.put(
    "/{user_id}",
    summary="Update a user",
    description="""Update an existing user's profile fields.

**Updatable fields:** `name`, `phone`, `avatar_url`

**Note:** This endpoint does **not** update passwords or email. Use the dedicated
password-change endpoint for that.

Requires authentication.
""",
    responses={
        200: {
            "description": "User updated successfully",
            "content": {
                "application/json": {
                    "examples": {"success": USER_UPDATED_EXAMPLE}
                }
            }
        },
        400: {"description": "Duplicate email or validation error"},
        404: {"description": "User not found"},
        401: {"description": "Authentication required"},
    },
)
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


@router.delete(
    "/{user_id}",
    summary="Delete a user",
    description="""Permanently delete a user by ID.

This removes the user record from the database. This action cannot be undone.

Requires authentication.
""",
    responses={
        200: {
            "description": "User deleted successfully",
            "content": {
                "application/json": {
                    "examples": {"success": USER_DELETED_EXAMPLE}
                }
            }
        },
        404: {"description": "User not found"},
        401: {"description": "Authentication required"},
    },
)
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
