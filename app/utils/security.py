"""
Security utilities for password hashing and JWT token management.
This modules includes functions to hash passwords, verify passwords,
- Password hashing with bcrypt
- JWT token generation and verification
- HTTP Bearer token extraction for protected routes
"""

from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from starlette.requests import Request
from app.config import settings

# ============================================================================
# PASSWORD HASHING CONFIGURATION
# ============================================================================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a plaintext password using bcrypt.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a bcrypt hash.
    """
    return pwd_context.verify(plain_password, hashed_password)


# ============================================================================
# JWT TOKEN MANAGEMENT
# ============================================================================


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a JWT (JSON Web Token) for user authentication.
    """

    to_encode = data.copy()

    # Determine token expiry time
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    # Add expiry time to payload
    to_encode.update({"exp": expire})

    # Encode and sign the token
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """
    Verify and decode a JWT token.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


# ============================================================================
# FASTAPI DEPENDENCY FOR PROTECTED ROUTES
# ============================================================================

# HTTPBearer extracts token from "Authorization: Bearer <token>" header
security = HTTPBearer()


async def get_current_user(request: Request) -> dict:
    """
    FastAPI dependency to verify JWT token from request headers.

    Use this in any endpoint you want to protect from unauthorized access.
    
    Args:
        request: The HTTP request object (FastAPI provides this automatically)
        
    Returns:
        dict: Token payload containing user info
        
    Raises:
        HTTPException 401: If token is missing, invalid, or expired
    """
    # Extract token from Authorization header
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if it starts with "Bearer "
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract the token
    token = auth_header.split(" ")[1]
    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract user_id from token payload
    # "sub" (subject) is standard JWT field for the user identifier
    user_id: Optional[str] = payload.get("sub")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token - missing user ID",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload
