"""
Authentication API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
    TwoFactorLoginRequest,
    TwoFactorVerifyRequest,
    UserWithRolesResponse
)
from app.services.auth_service import AuthService
from app.api.dependencies import get_current_user
from app.models.user import User
from app.utils.response import APIResponse


router = APIRouter(prefix="/auth", tags=["Authentication"])


# ---------------------------------------------------------------------------
# OpenAPI response examples — referenced in each route's `responses=` kwarg
# ---------------------------------------------------------------------------

_USER_EXAMPLE = {
    "id": 1,
    "name": "Admin User",
    "email": "admin@satryawiguna.me",
    "phone": "293789723",
    "avatar_url": "https://example.com/avatar.jpg",
    "isActive": True,
    "roles": [{"id": 1, "name": "Admin"}],
}

_TOKEN_DATA_EXAMPLE = {
    "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refreshToken": "6av_sUFU17n8ZowSH2-Cw5bmcxVDzt_KvMHwtfTQc831YIPqjM...",
    "tokenType": "Bearer",
    "expiresIn": "15m",
    "refreshExpiresIn": "7d",
    "user": _USER_EXAMPLE,
}

LOGIN_EXAMPLE = {
    "example": {
        "success": True,
        "status": 200,
        "message": "Login successful",
        "data": _TOKEN_DATA_EXAMPLE,
        "timestamp": "2026-03-27T07:58:24.734Z",
    }
}

REFRESH_EXAMPLE = {
    "example": {
        "success": True,
        "status": 200,
        "message": "Token refreshed successfully",
        "data": _TOKEN_DATA_EXAMPLE,
        "timestamp": "2026-03-27T07:58:24.734Z",
    }
}

ME_EXAMPLE = {
    "example": {
        "success": True,
        "status": 200,
        "message": "User retrieved successfully",
        "data": _USER_EXAMPLE,
        "timestamp": "2026-03-27T07:58:24.734Z",
    }
}

LOGOUT_EXAMPLE = {
    "example": {
        "success": True,
        "status": 200,
        "message": "Logout successful",
        "timestamp": "2026-03-27T07:58:24.734Z",
    }
}

CHANGE_PASSWORD_EXAMPLE = {
    "example": {
        "success": True,
        "status": 200,
        "message": "Password changed successfully",
        "timestamp": "2026-03-27T07:58:24.734Z",
    }
}

FORGOT_PASSWORD_EXAMPLE = {
    "example": {
        "success": True,
        "status": 200,
        "message": "Password reset email sent",
        "timestamp": "2026-03-27T07:58:24.734Z",
    }
}

RESET_PASSWORD_EXAMPLE = {
    "example": {
        "success": True,
        "status": 200,
        "message": "Password reset successful",
        "timestamp": "2026-03-27T07:58:24.734Z",
    }
}


@router.post(
    "/login",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "Login successful",
            "content": {
                "application/json": LOGIN_EXAMPLE
            }
        }
    }
)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Login with email and password
    
    - **email**: User email address
    - **password**: User password
    
    Returns JWT access token
    """
    auth_service = AuthService(db)

    user = await auth_service.authenticate_user(request.email, request.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = auth_service.generate_access_token(user)
    refresh_token = await auth_service.issue_refresh_token(user.id)
    user_with_roles = auth_service.get_user_with_roles(user)

    token_response = TokenResponse(
        accessToken=access_token,
        refreshToken=refresh_token,
        user=user_with_roles,
    )

    return APIResponse.success(
        message="Login successful",
        data=token_response.model_dump(),
    )


@router.post(
    "/login/2fa",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "OTP sent successfully"},
        400: {"description": "Bad request - User not found or inactive"},
    }
)
async def login_2fa(
    request: TwoFactorLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Request OTP for 2FA login
    
    - **email**: User email address
    
    Generates a 6-digit OTP and sends it to the user's email.
    The OTP must be verified using the /auth/verify/2fa endpoint.
    
    Returns 204 No Content on success, 400 Bad Request if user not found or inactive.
    """
    auth_service = AuthService(db)

    try:
        await auth_service.send_2fa_otp(request.email)
        # Return 204 No Content - no response body
        return None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/verify/2fa",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "OTP verified successfully - Login successful",
            "content": {
                "application/json": LOGIN_EXAMPLE
            }
        },
        400: {"description": "Invalid OTP or user not found"},
    }
)
async def verify_2fa(
    request: TwoFactorVerifyRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Verify OTP and complete 2FA login
    
    - **email**: User email address
    - **otp**: 6-digit OTP code received via email
    
    Verifies the OTP and returns JWT access token if valid.
    The OTP is cleared after successful verification.
    """
    auth_service = AuthService(db)

    try:
        user = await auth_service.verify_2fa_otp(request.email, request.otp)
        
        # Generate tokens
        access_token = auth_service.generate_access_token(user)
        refresh_token = await auth_service.issue_refresh_token(user.id)
        user_with_roles = auth_service.get_user_with_roles(user)

        token_response = TokenResponse(
            accessToken=access_token,
            refreshToken=refresh_token,
            user=user_with_roles,
        )

        return APIResponse.success(
            message="Login successful",
            data=token_response.model_dump(),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/refresh",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Token refreshed successfully", "content": {"application/json": REFRESH_EXAMPLE}},
        401: {"description": "Invalid, revoked, or expired refresh token"},
    },
)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Refresh access token using refresh token
    
    - **refreshToken**: Valid refresh token
    
    Returns new JWT access token and refresh token
    """
    auth_service = AuthService(db)

    result = await auth_service.refresh_access_token(request.refreshToken)

    user_with_roles = auth_service.get_user_with_roles(result["user"])

    token_response = TokenResponse(
        accessToken=result["access_token"],
        refreshToken=result["refresh_token"],
        user=user_with_roles,
    )

    return APIResponse.success(
        message="Token refreshed successfully",
        data=token_response.model_dump(),
    )


@router.get(
    "/me",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Current user retrieved successfully", "content": {"application/json": ME_EXAMPLE}},
        401: {"description": "Invalid or expired access token"},
    },
)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current authenticated user information
    
    Requires valid JWT access token in Authorization header:
    ```
    Authorization: Bearer <access_token>
    ```
    
    Returns user information with roles
    """
    auth_service = AuthService(db)
    
    # Get user with roles
    user_with_roles = auth_service.get_user_with_roles(current_user)
    
    return APIResponse.success(
        message="User retrieved successfully",
        data=user_with_roles.model_dump()
    )


@router.post(
    "/logout",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Logout successful", "content": {"application/json": LOGOUT_EXAMPLE}},
        400: {"description": "Invalid refresh token"},
        401: {"description": "Invalid or expired access token"},
    },
)
async def logout(
    request: RefreshTokenRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Logout user by revoking refresh token
    
    - **refreshToken**: Refresh token to revoke
    
    Requires valid JWT access token in Authorization header
    """
    auth_service = AuthService(db)

    success = await auth_service.logout(request.refreshToken)
    
    if success:
        return APIResponse.success(
            message="Logout successful"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid refresh token"
        )


@router.post(
    "/forgot-password",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Password reset email sent", "content": {"application/json": FORGOT_PASSWORD_EXAMPLE}},
    },
)
async def forgot_password(
    request: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Request password reset
    
    - **email**: User email address
    
    Sends password reset link to user's email (not implemented yet)
    """
    # TODO: Implement password reset email sending
    return APIResponse.success(
        message="Password reset email sent (not implemented)"
    )


@router.post(
    "/reset-password",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Password reset successful", "content": {"application/json": RESET_PASSWORD_EXAMPLE}},
        400: {"description": "Passwords do not match"},
    },
)
async def reset_password(
    request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Reset password with token
    
    - **token**: Password reset token from email
    - **password**: New password
    - **passwordConfirmation**: Password confirmation
    
    Resets user password (not implemented yet)
    """
    # TODO: Implement password reset logic
    if request.password != request.passwordConfirmation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    return APIResponse.success(
        message="Password reset successful (not implemented)"
    )


@router.post(
    "/change-password",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Password changed successfully", "content": {"application/json": CHANGE_PASSWORD_EXAMPLE}},
        400: {"description": "Current password incorrect or new passwords do not match"},
        401: {"description": "Invalid or expired access token"},
    },
)
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Change user password
    
    - **currentPassword**: Current password
    - **newPassword**: New password
    - **newPasswordConfirmation**: New password confirmation
    
    Requires valid JWT access token in Authorization header
    """
    if request.newPassword != request.newPasswordConfirmation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New passwords do not match",
        )

    auth_service = AuthService(db)
    await auth_service.change_password(
        user=current_user,
        current_password=request.currentPassword,
        new_password=request.newPassword,
    )

    return APIResponse.success(message="Password changed successfully")
