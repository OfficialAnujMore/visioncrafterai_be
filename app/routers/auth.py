from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from datetime import datetime, timezone

from app.schemas import GoogleAuthRequest, UserResponse, AuthResponse
from app.schemas.common import ApiResponse
from app.models import User
from app.database import get_session
from app.utils import verify_google_token, create_access_token
from app.locale import AUTH_MESSAGES

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/google", response_model=ApiResponse[AuthResponse])
async def google_auth(
    auth_data: GoogleAuthRequest, session: AsyncSession = Depends(get_session)
) -> ApiResponse[AuthResponse]:
    """
    Authenticate user with Google OAuth token.
    Creates a new user if they don't exist, or logs in existing user.

    Args:
        auth_data: Contains Google ID token from frontend
        session: Database session (FastAPI provides automatically)

    Returns:
        AuthResponse: JWT access token and user info

    Raises:
        HTTPException 401: If Google token is invalid
    """
    # Verify Google token and get user info
    google_user_info = await verify_google_token(auth_data.token)
    
    # Check if user exists
    statement = select(User).where(User.google_id == google_user_info['google_id'])
    result = await session.execute(statement)
    user = result.scalars().first()
    
    if user:
        # User exists - update last login
        user.last_login = datetime.now(timezone.utc).replace(tzinfo=None)
        session.add(user)
        await session.commit()
        await session.refresh(user)
    else:
        # New user - create account
        user = User(
            google_id=google_user_info['google_id'],
            email=google_user_info['email'],
            name=google_user_info['name'],
            picture=google_user_info.get('picture'),
            is_active=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
    
    # Create JWT access token
    access_token = create_access_token(user.id)
    
    auth_response = AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            google_id=user.google_id,
            email=user.email,
            name=user.name,
            picture=user.picture,
            is_active=user.is_active,
            created_at=user.created_at,
        )
    )
    
    return ApiResponse(
        success=True,
        message="Authentication successful",
        data=auth_response
    )