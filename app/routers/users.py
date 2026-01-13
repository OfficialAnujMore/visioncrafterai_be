"""
User profile management endpoints
These endpoints are protected - user must be authenticated
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.schemas import UserResponse, UserUpdateRequest
from app.models import User
from app.database import get_session
from app.utils import get_current_user
from app.locale import USER_MESSAGES

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/profile", response_model=UserResponse)
async def get_profile(
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> UserResponse:
    """
    Get current authenticated user's profile.

    Args:
        current_user: Verified JWT token payload (contains user_id)
        session: Async database session

    Returns:
        UserResponse: User's profile information

    """

    # Extract user_id from token payload
    user_id = int(current_user["sub"])

    # Query database
    statement = select(User).where(User.id == user_id)
    result = await session.execute(statement)
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=USER_MESSAGES["user_not_found"]
        )

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active,
        created_at=user.created_at,
    )


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    update_data: UserUpdateRequest,
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> UserResponse:
    """
    Update current user's profile.

    Args:
        update_data: New first_name and/or last_name
        current_user: Verified JWT token payload
        session: Async database session

    Returns:
        UserResponse: Updated user information

    What can be updated:
    - first_name: User's first name
    - last_name: User's last name
    """

    user_id = int(current_user["sub"])
    statement = select(User).where(User.id == user_id)
    result = await session.execute(statement)
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=USER_MESSAGES["user_not_found"]
        )

    # Update only provided fields
    if update_data.first_name is not None:
        user.first_name = update_data.first_name
    if update_data.last_name is not None:
        user.last_name = update_data.last_name

    try:
        session.add(user)
        await session.commit()
        await session.refresh(user)
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=USER_MESSAGES["profile_update_failed"],
        )

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active,
        created_at=user.created_at,
    )
