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


def create_access_token(user_id: int) -> str:
    """
    Create a JWT access token for authenticated user.
    
    Args:
        user_id: The user's database ID
        
    Returns:
        str: JWT access token
    """
    to_encode = {"sub": str(user_id)}
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
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
