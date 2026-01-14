from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from datetime import datetime, timezone

from app.schemas import GoogleAuthRequest, AuthResponse, UserResponse
from app.models import User
from app.database import get_session
from app.utils import verify_google_token, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/google", response_model=AuthResponse)
async def google_auth(
    auth_data: GoogleAuthRequest,
    session: AsyncSession = Depends(get_session)
) -> AuthResponse:
    """
    Authenticate user with Google OAuth token.
    
    Flow:
    1. Verify Google token and extract user info
    2. Check if user exists in database (by google_id)
    3. If new user, create account
    4. If existing user, update last_login
    5. Generate JWT access token
    6. Return token and user info
    
    Args:
        auth_data: Contains Google ID token
        session: Database session
        
    Returns:
        AuthResponse: JWT token and user information
        
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
        # Existing user - update last login
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
            picture=google_user_info['picture'],
            is_active=True
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
    
    # Generate JWT access token
    access_token = create_access_token(user.id)
    
    # Return authentication response
    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            google_id=user.google_id,
            email=user.email,
            name=user.name,
            picture=user.picture,
            is_active=user.is_active,
            created_at=user.created_at
        )
    )
