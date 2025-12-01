from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    TokenResponse,
)
from app.models import User
from app.database import get_session
from app.utils import hash_password, verify_password, create_access_token
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserRegisterRequest, session: Session = Depends(get_session)
) -> UserResponse:
    """
    Register a new user account.

    Args:
        user_data: Contains username, email, password, full_name
        session: Database session (FastAPI provides automatically)

    Returns:
        UserResponse: The created user (without password)

    Raises:
        HTTPException 400: If email or username already exists
    """

    hashed_password = hash_password(user_data.password)

    db_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        is_active=True,
    )

    try:
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

        return UserResponse(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            full_name=db_user.full_name,
            is_active=db_user.is_active,
            created_at=db_user.created_at,
        )

    except IntegrityError:
        # Email or username already exists (unique constraint violated)
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered",
        )
    except Exception as e:

        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user",
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLoginRequest, session: Session = Depends(get_session)
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
    user = session.exec(statement).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )
    
    access_token = create_access_token(
        data={"sub": str(user.id)}
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at
        )
        )
