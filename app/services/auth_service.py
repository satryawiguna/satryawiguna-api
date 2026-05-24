"""
Authentication service
"""
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError, BusinessLogicError
from app.models.user import User, RefreshToken
from app.repositories.user_repository import UserRepository, RefreshTokenRepository
from app.core.security import (
    verify_password,
    hash_password,
    create_access_token,
    create_refresh_token as generate_refresh_token_string,
    generate_otp,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
)
from app.schemas.auth import UserWithRolesResponse, RoleResponse
from app.utils.email import send_otp_email


class AuthService:
    """Service for authentication operations"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repository = UserRepository(db)
        self.refresh_token_repository = RefreshTokenRepository(db)

    # ------------------------------------------------------------------
    # User authentication
    # ------------------------------------------------------------------

    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Validate email/password credentials.

        Returns the User on success, or None if credentials are wrong
        or the account is inactive.
        """
        user = await self.user_repository.get_by_email(email)

        if not user:
            return None

        if not verify_password(password, user.password):
            return None

        if not user.is_active:
            return None

        return user

    # ------------------------------------------------------------------
    # Token management
    # ------------------------------------------------------------------

    def generate_access_token(self, user: User) -> str:
        """Create a short-lived JWT access token for the given user."""
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "type": "access",
        }
        return create_access_token(token_data)

    # Keep the old name as an alias so existing call-sites don't break.
    def generate_token(self, user: User) -> str:
        return self.generate_access_token(user)

    async def issue_refresh_token(self, user_id: int) -> str:
        """
        Generate a secure random refresh token, persist it, and return the
        raw token string.  Tokens are valid for REFRESH_TOKEN_EXPIRE_DAYS.
        """
        token_string = generate_refresh_token_string()
        expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

        record = RefreshToken(
            token=token_string,
            user_id=user_id,
            expires_at=expires_at,
        )
        await self.refresh_token_repository.create(record)
        return token_string

    async def refresh_access_token(self, refresh_token_str: str) -> dict:
        """
        Validate a refresh token, rotate it (revoke old, issue new), and
        return a dict with the new access token, new refresh token, and user.

        Raises AuthenticationError if the token is invalid, revoked, or expired.
        """
        record = await self.refresh_token_repository.find_by_token(refresh_token_str)

        if not record:
            raise AuthenticationError("Invalid refresh token")

        if record.revoked:
            raise AuthenticationError("Refresh token has been revoked")

        if record.expires_at < datetime.utcnow():
            raise AuthenticationError("Refresh token has expired")

        user = await self.user_repository.get_by_id(record.user_id)

        if not user or not user.is_active:
            raise AuthenticationError("User not found or inactive")

        # Token rotation — revoke the consumed token before issuing a new one.
        await self.refresh_token_repository.revoke(refresh_token_str)

        new_access_token = self.generate_access_token(user)
        new_refresh_token = await self.issue_refresh_token(user.id)

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "user": user,
        }

    async def logout(self, refresh_token_str: str) -> bool:
        """
        Revoke a refresh token.  Returns True if the token existed and was
        revoked, False if it was not found.
        """
        return await self.refresh_token_repository.revoke(refresh_token_str)

    # ------------------------------------------------------------------
    # Password management
    # ------------------------------------------------------------------

    async def change_password(
        self, user: User, current_password: str, new_password: str
    ) -> None:
        """
        Verify the current password, then update to the new one.
        All active refresh tokens are revoked so existing sessions are
        invalidated after a password change.

        Raises BusinessLogicError if the current password is wrong.
        """
        if not verify_password(current_password, user.password):
            raise BusinessLogicError("Current password is incorrect")

        user.password = hash_password(new_password)
        await self.user_repository.update(user)

        # Force re-login on all devices after password change.
        await self.refresh_token_repository.revoke_all_for_user(user.id)

    # ------------------------------------------------------------------
    # 2FA (Two-Factor Authentication)
    # ------------------------------------------------------------------

    async def send_2fa_otp(self, email: str) -> bool:
        """
        Generate and send OTP to user's email for 2FA login.
        Only sends the email if the user's email is verified.

        Args:
            email: User's email address

        Returns:
            True if OTP was generated and sent successfully

        Raises:
            AuthenticationError: If user not found, inactive, or email not verified
        """
        user = await self.user_repository.get_by_email(email)

        if not user:
            raise AuthenticationError("User not found")

        if not user.is_active:
            raise AuthenticationError("User account is inactive")

        # Check email verification — only send OTP if email is verified
        if not user.email_verified_at:
            raise AuthenticationError(
                "Email not verified. Please verify your email before requesting OTP."
            )

        # Generate 6-digit OTP
        otp = generate_otp(6)

        # Store OTP in user table
        user.otp = otp
        await self.user_repository.update(user)

        # Send OTP via email
        email_sent = await send_otp_email(email, otp)

        if not email_sent:
            raise BusinessLogicError("Failed to send OTP email")

        return True
    
    async def verify_2fa_otp(self, email: str, otp: str) -> User:
        """
        Verify OTP and return user if valid.
        
        Args:
            email: User's email address
            otp: OTP code to verify
            
        Returns:
            User object if OTP is valid
            
        Raises:
            AuthenticationError: If user not found, inactive, or OTP is invalid
        """
        user = await self.user_repository.get_by_email(email)
        
        if not user:
            raise AuthenticationError("User not found")
        
        if not user.is_active:
            raise AuthenticationError("User account is inactive")
        
        if not user.otp:
            raise AuthenticationError("No OTP found. Please request a new one")
        
        if user.otp != otp:
            raise AuthenticationError("Invalid OTP code")
        
        # Clear OTP after successful verification
        user.otp = None
        await self.user_repository.update(user)
        
        return user

    # ------------------------------------------------------------------
    # Response helpers
    # ------------------------------------------------------------------

    def get_user_with_roles(self, user: User) -> UserWithRolesResponse:
        """Build the UserWithRolesResponse from a User ORM instance."""
        roles = [
            RoleResponse(id=ur.role.id, name=ur.role.name)
            for ur in user.user_roles
        ]
        return UserWithRolesResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            phone=user.phone,
            avatar_url=user.avatar_url,
            isActive=user.is_active,
            roles=roles,
        )
