"""
Authentication schemas
"""
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime


class RoleResponse(BaseModel):
    """Role response schema"""
    id: int
    name: str
    
    class Config:
        from_attributes = True


class UserWithRolesResponse(BaseModel):
    """User response with roles"""
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    isActive: bool
    roles: List[RoleResponse]
    
    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response schema"""
    accessToken: str
    refreshToken: Optional[str] = None
    tokenType: str = "Bearer"
    expiresIn: str = "15m"
    refreshExpiresIn: str = "7d"
    user: UserWithRolesResponse


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""
    refreshToken: str


class ForgotPasswordRequest(BaseModel):
    """Forgot password request schema"""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Reset password request schema"""
    token: str
    password: str
    passwordConfirmation: str


class ChangePasswordRequest(BaseModel):
    """Change password request schema"""
    currentPassword: str
    newPassword: str
    newPasswordConfirmation: str


class TwoFactorLoginRequest(BaseModel):
    """2FA Login request schema"""
    email: EmailStr


class TwoFactorVerifyRequest(BaseModel):
    """2FA Verify request schema"""
    email: EmailStr
    otp: str


class SendOtpRequest(BaseModel):
    """Send OTP request schema"""
    email: EmailStr
    phone: Optional[str] = None


class VerifyOtpRequest(BaseModel):
    """Verify OTP request schema"""
    email: EmailStr
    otp: str


class VerifyOtpResponse(BaseModel):
    """Verify OTP response schema"""
    success: bool
    message: str
    emailVerified: bool = False
