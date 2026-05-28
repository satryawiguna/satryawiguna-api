"""
API dependencies for authentication
"""
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.core.security import decode_access_token
from app.models.user import User
from app.repositories.user_repository import UserRepository


# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials

    payload = decode_access_token(token)

    if payload is None:
        raise AuthenticationError("Invalid or expired token")

    user_id = payload.get("sub")

    if user_id is None:
        raise AuthenticationError("Invalid token payload")

    user_repository = UserRepository(db)
    user = await user_repository.get_by_id(int(user_id))

    if user is None:
        raise AuthenticationError("User not found")

    if not user.is_active:
        raise AuthorizationError("User is not active")

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    return current_user
