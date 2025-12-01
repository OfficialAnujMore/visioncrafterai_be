"""
User profile management endpoints
These endpoints are protected - user must be authenticated
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.schemas import UserResponse, UserUpdateRequest
from app.models import User
from app.database import get_session
from app.utils import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/profile", response_model=UserResponse)
async def get_profile(
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> UserResponse:
    """
    Get current authenticated user's profile.

    Args:
        current_user: Verified JWT token payload (contains user_id)
        session: Database session

    Returns:
        UserResponse: User's profile information

    """

    # Extract user_id from token payload
    user_id = int(current_user["sub"])

    # Query database
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        created_at=user.created_at,
    )


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    update_data: UserUpdateRequest,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> UserResponse:
    """
    Update current user's profile.

    Args:
        update_data: New full_name
        current_user: Verified JWT token payload
        session: Database session

    Returns:
        UserResponse: Updated user information

    What can be updated:
    - full_name: User's full name
    - email: User's email address
    """

    user_id = int(current_user["sub"])
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update only provided fields
    if update_data.full_name is not None:
        user.full_name = update_data.full_name

    try:
        session.add(user)
        session.commit()
        session.refresh(user)
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )
    
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        created_at=user.created_at
    )