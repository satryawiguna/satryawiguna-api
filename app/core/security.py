"""
Security utilities for password hashing and JWT
"""
from datetime import datetime, timedelta
from typing import Optional, Dict
from passlib.context import CryptContext
from jose import JWTError, jwt
import secrets
import random

from app.core.config import settings


# Password hashing context
# Using explicit rounds to avoid bcrypt compatibility issues
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
    bcrypt__ident="2b"
)

# Token expiration constants
ACCESS_TOKEN_EXPIRE_MINUTES = 15  # 15 minutes
REFRESH_TOKEN_EXPIRE_DAYS = 7  # 7 days


def hash_password(password: str) -> str:
    """
    Hash a plain password
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token
    
    Args:
        data: Data to encode in token
        expires_delta: Token expiration time
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


def create_refresh_token() -> str:
    """
    Create a secure random refresh token
    
    Returns:
        Random token string
    """
    return secrets.token_urlsafe(64)


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode JWT access token
    
    Args:
        token: JWT token
        
    Returns:
        Decoded token data or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def create_tokens(user_id: int, email: str) -> Dict[str, str]:
    """
    Create both access and refresh tokens for a user
    
    Args:
        user_id: User ID
        email: User email
        
    Returns:
        Dictionary with access_token and refresh_token
    """
    # Create access token with user claims
    access_token_data = {
        "sub": str(user_id),
        "email": email,
        "type": "access"
    }
    access_token = create_access_token(access_token_data)
    
    # Create refresh token
    refresh_token = create_refresh_token()
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }


def generate_otp(length: int = 6) -> str:
    """
    Generate a random OTP (One-Time Password)
    
    Args:
        length: Length of the OTP (default: 6)
        
    Returns:
        OTP string of specified length
    """
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])
