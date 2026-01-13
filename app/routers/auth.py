from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from datetime import timedelta, datetime, timezone

from app.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    TokenResponse,
    RefreshTokenRequest,
)
from app.models import User, RefreshToken
from app.database import get_session
from app.utils import (
    hash_password, 
    verify_password, 
    verify_refresh_token,
    create_token_pair
)
from app.config import settings
from app.locale import AUTH_MESSAGES

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse)
async def register(
    user_data: UserRegisterRequest, session: AsyncSession = Depends(get_session)
) -> TokenResponse:
    """
    Register a new user account and return JWT tokens.

    Args:
        user_data: Contains username, email, password, first_name, last_name
        session: Database session (FastAPI provides automatically)

    Returns:
        TokenResponse: JWT tokens and user info

    Raises:
        HTTPException 400: If email or username already exists
    """
    print("User data", user_data)
    hashed_password = hash_password(user_data.password)

    db_user = User(
        username=user_data.username,
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        hashed_password=hashed_password,
        is_active=True,
    )

    try:
        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)

        # Create both access and refresh tokens
        token_pair = create_token_pair(db_user.id)
        
        # Store refresh token in database for tracking and revocation
        refresh_token_record = RefreshToken(
            user_id=db_user.id,
            token=token_pair["refresh_token"],
            expires_at=(datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)).replace(tzinfo=None)
        )
        session.add(refresh_token_record)
        await session.commit()

        return TokenResponse(
            access_token=token_pair["access_token"],
            refresh_token=token_pair["refresh_token"],
            token_type="bearer",
            user=UserResponse(
                id=db_user.id,
                username=db_user.username,
                email=db_user.email,
                first_name=db_user.first_name,
                last_name=db_user.last_name,
                is_active=db_user.is_active,
                created_at=db_user.created_at,
            )
        )

    except IntegrityError:
        # Email or username already exists (unique constraint violated)
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=AUTH_MESSAGES["email_already_exists"],
        )
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=AUTH_MESSAGES["registration_failed"],
        )

@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLoginRequest, session: AsyncSession = Depends(get_session)
) -> TokenResponse:
    """
    Authenticate user and return JWT token.

    Args:
        credentials: Contains email and password
        session: Database session (FastAPI provides automatically)

    Returns:
        TokenResponse: JWT token + user info

    Raises:
        HTTPException 401: If email not found or password incorrect
    """

    statement = select(User).where(User.email == credentials.email)
    result = await session.execute(statement)
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=AUTH_MESSAGES["invalid_credentials"]
        )

    print(f"Login attempt for user: {user.email}")
    print(f"Password from request: {credentials.password}")
    password_valid = verify_password(credentials.password, user.hashed_password)
    print(f"Password verification result: {password_valid}")
    
    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=AUTH_MESSAGES["invalid_credentials"]
        )
    
    # Create both access and refresh tokens
    token_pair = create_token_pair(user.id)
    
    # Store refresh token in database for tracking and revocation
    refresh_token_record = RefreshToken(
        user_id=user.id,
        token=token_pair["refresh_token"],
        expires_at=(datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)).replace(tzinfo=None)
    )
    session.add(refresh_token_record)
    await session.commit()

    return TokenResponse(
        access_token=token_pair["access_token"],
        refresh_token=token_pair["refresh_token"],
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            created_at=user.created_at
        )
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    request: RefreshTokenRequest, session: AsyncSession = Depends(get_session)
) -> TokenResponse:
    """
    Refresh access token using a valid refresh token.
    
    Args:
        request: Contains the refresh_token
        session: Database session
        
    Returns:
        TokenResponse: New access_token and refresh_token
        
    Raises:
        HTTPException 401: If refresh token is invalid/expired
    """
    # Verify the refresh token and get user_id
    user_id = verify_refresh_token(request.refresh_token)
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=AUTH_MESSAGES["refresh_token_invalid"]
        )
    
    # Get user from database
    statement = select(User).where(User.id == user_id)
    result = await session.execute(statement)
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=AUTH_MESSAGES["invalid_credentials"]
        )
    
    # Create new token pair
    token_pair = create_token_pair(user_id)
    
    # Store new refresh token in database
    refresh_token_record = RefreshToken(
        user_id=user_id,
        token=token_pair["refresh_token"],
        expires_at=(datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)).replace(tzinfo=None)
    )
    session.add(refresh_token_record)
    
    try:
        await session.commit()
    except IntegrityError:
        # Token already exists (rare but possible if refresh called twice in same second)
        await session.rollback()
        # Continue anyway - token is still valid
    
    return TokenResponse(
        access_token=token_pair["access_token"],
        refresh_token=token_pair["refresh_token"],
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            created_at=user.created_at
        )
    )