"""
Security utilities for JWT token management and Google OAuth verification
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

import httpx

from app.config import settings


security = HTTPBearer()


def create_access_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token for authenticated user.
    
    Args:
        user_id: The user's database ID
        expires_delta: Optional custom expiration time (default: ACCESS_TOKEN_EXPIRE_MINUTES)
        
    Returns:
        str: JWT access token
    """
    to_encode = {"sub": str(user_id), "type": "access"}
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT refresh token for authenticated user.
    Refresh tokens have a longer expiration time (7 days).
    
    Args:
        user_id: The user's database ID
        expires_delta: Optional custom expiration time (default: 7 days)
        
    Returns:
        str: JWT refresh token
    """
    to_encode = {"sub": str(user_id), "type": "refresh"}
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=7)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token to verify
        
    Returns:
        dict: Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


async def verify_google_token(token: str) -> dict:
    """
    Verify Google ID token and extract user information.
    
    Args:
        token: Google ID token from frontend
        
    Returns:
        dict: User info from Google (google_id, email, name, picture)
        
    Raises:
        HTTPException: If token is invalid
    """
    try:
        # Use Google's tokeninfo endpoint to verify the token
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://oauth2.googleapis.com/tokeninfo?id_token={token}"
            )
            
            if response.status_code != 200:
                raise ValueError("Invalid token")
            
            token_info = response.json()
            
            # Verify the token is for our app
            if token_info.get('aud') != settings.GOOGLE_CLIENT_ID:
                raise ValueError("Token is for a different application")
            
            # Extract user information
            return {
                'google_id': token_info['sub'],
                'email': token_info['email'],
                'name': token_info.get('name', ''),
                'picture': token_info.get('picture', '')
            }
        
    except (ValueError, KeyError, httpx.HTTPError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google token: {str(e)}"
        )


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer token from request header
        
    Returns:
        dict: Token payload containing user_id
        
    Raises:
        HTTPException: If token is invalid or missing
    """
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload


def get_token_from_request(request) -> tuple[Optional[str], Optional[str]]:
    """
    Extract access_token and refresh_token from request cookies.
    
    Args:
        request: FastAPI Request object
        
    Returns:
        tuple: (access_token, refresh_token) or (None, None)
    """
    access_token = request.cookies.get("access_token")
    refresh_token = request.cookies.get("refresh_token")
    return access_token, refresh_token


async def verify_token_type(token: str, expected_type: str = "access") -> dict:
    """
    Verify token and check its type (access or refresh).
    
    Args:
        token: JWT token to verify
        expected_type: Expected token type ("access" or "refresh")
        
    Returns:
        dict: Token payload
        
    Raises:
        HTTPException: If token is invalid or wrong type
    """
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired {expected_type} token",
        )
    
    # Check token type
    token_type = payload.get("type", "access")
    if token_type != expected_type:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token type. Expected {expected_type}, got {token_type}",
        )
    
    return payload
