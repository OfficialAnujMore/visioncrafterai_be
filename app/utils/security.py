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
# JWT ACCESS TOKEN MANAGEMENT
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
# JWT REFRESH TOKEN MANAGEMENT
# ============================================================================
def create_refresh_token(user_id: int) -> str:
    """
    Create a refresh token JWT for a user.

    Args:
        user_id: The user's ID

    Returns:
        str: The refresh token JWT
    """

    to_encode = {"sub": str(user_id), "type": "refresh"}
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def verify_refresh_token(token: str) -> Optional[int]:
    """
    Verify and decode a refresh token, return user_id.

    Args:
        token: The refresh token to verify

    Returns:
        int: User ID if valid, None if invalid
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM]
        )

        # Check token type
        if payload.get("type") != "refresh":
            return None

        user_id: Optional[str] = payload.get("sub")
        return int(user_id) if user_id else None
    except JWTError:
        return None

# ============================================================================
# JWT TOKEN MANAGEMENT
# ============================================================================
def create_token_pair(user_id: int) -> dict:
    """
    Create both access and refresh tokens for a user.

    Args:
        user_id: The user's ID

    Returns:
        dict: Contains 'access_token' and 'refresh_token'
    """
    access_token = create_access_token({"sub": str(user_id)})
    refresh_token = create_refresh_token(user_id)

    return {"access_token": access_token, "refresh_token": refresh_token}


# ============================================================================
# FASTAPI DEPENDENCY FOR PROTECTED ROUTES
# ============================================================================

# HTTPBearer extracts token from "Authorization: Bearer <token>" header
security = HTTPBearer()


async def get_current_user(credentials=Depends(security)) -> dict:
    """
    FastAPI dependency to verify JWT token from request headers.

    Use this in any endpoint you want to protect from unauthorized access.

    Args:
        credentials: HTTPAuthCredentials from Authorization header (FastAPI provides automatically)

    Returns:
        dict: Token payload containing user info

    Raises:
        HTTPException 401: If token is missing, invalid, or expired
    """
    # Extract token from credentials object
    token = credentials.credentials

    # Verify the token
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
