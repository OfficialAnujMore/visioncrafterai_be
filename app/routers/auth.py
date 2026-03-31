from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from datetime import datetime, timezone, timedelta

from app.schemas import GoogleAuthRequest, UserResponse, AuthResponse
from app.schemas.common import ApiResponse
from app.models import User
from app.database import get_session
from app.utils import verify_google_token, create_access_token, create_refresh_token, verify_token_type
from app.locale import AUTH_MESSAGES
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/google")
async def google_auth(
    auth_data: GoogleAuthRequest, 
    session: AsyncSession = Depends(get_session)
):
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
    try:
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
        
        # ✅ Create TWO tokens: short-lived access + long-lived refresh
        access_token = create_access_token(
            user.id, 
            expires_delta=timedelta(minutes=15)  # 15 minutes
        )
        refresh_token = create_refresh_token(
            user.id,
            expires_delta=timedelta(days=7)  # 7 days
        )

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
        
        # Create response object with success message
        response_data = ApiResponse(
            success=True,
            message="Authentication successful",
            data=auth_response
        )
        
        # Create JSONResponse to set cookies
        # Use mode='json' to properly serialize datetime objects
        response = JSONResponse(
            content=response_data.model_dump(mode='json'),
            status_code=200
        )
        
        # Set HttpOnly, Secure, SameSite cookies for BOTH tokens
        
        # ✅ Access token cookie (short-lived)
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,  # Prevents JavaScript access (XSS protection)
            secure=not settings.DEBUG,  # Only HTTPS in production
            samesite="lax",  # CSRF protection
            max_age=900,  # 15 minutes
            path="/",
        )
        
        # ✅ Refresh token cookie (long-lived)
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,  # Prevents JavaScript access
            secure=not settings.DEBUG,  # Only HTTPS in production
            samesite="lax",  # CSRF protection
            max_age=604800,  # 7 days
            path="/",
        )
                
        return response
        
    except Exception as e:
        raise


@router.post("/refresh")
async def refresh_access_token(request: Request):
    """
    Refresh the access token using the refresh token from cookies.
    Called when access token expires (401 error).
    
    Args:
        request: FastAPI Request object (contains cookies)
        
    Returns:
        ApiResponse: New access token
        
    Raises:
        HTTPException 401: If refresh token is invalid or expired
    """
    try:
        print("🔄 [AUTH] Refresh token requested")
        
        # Extract refresh token from cookies
        refresh_token = request.cookies.get("refresh_token")
        if not refresh_token:
            print("❌ [AUTH] No refresh token found in cookies")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token not found"
            )
        
        # Verify refresh token and check type
        payload = await verify_token_type(refresh_token, expected_type="refresh")
        user_id = int(payload.get("sub"))
        
        print(f"✓ [AUTH] Refresh token valid for user_id: {user_id}")
        
        # Create new access token
        new_access_token = create_access_token(
            user_id,
            expires_delta=timedelta(minutes=15)
        )
        
        print(f"✓ [AUTH] New access token created for user_id: {user_id}")
        
        # Return response with new access token
        response = JSONResponse(
            content=ApiResponse(
                success=True,
                message="Token refreshed successfully",
                data={"access_token": new_access_token}
            ).model_dump(mode='json'),
            status_code=200
        )
        
        # Set new access token cookie
        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=True,
            secure=not settings.DEBUG,
            samesite="lax",
            max_age=900,  # 15 minutes
            path="/",
        )
        
        print(f"✓ [AUTH] New access token cookie set, expires in 15 minutes")
        return response
        
    except Exception as e:
        print(f"❌ [AUTH] Error during token refresh: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token refresh failed: Invalid or expired refresh token"
        )


@router.post("/logout")
async def logout():
    """
    Logout endpoint - clears both access and refresh token cookies.
    
    Returns:
        ApiResponse: Logout success message
    """
    response = JSONResponse(
        content=ApiResponse(
            success=True,
            message="Logged out successfully"
        ).model_dump(mode='json'),
        status_code=200
    )
    
    # ✅ Delete BOTH cookies
    response.delete_cookie(
        key="access_token",
        path="/",
        httponly=True,
        samesite="lax",
        secure=not settings.DEBUG,
    )
    
    response.delete_cookie(
        key="refresh_token",
        path="/",
        httponly=True,
        samesite="lax",
        secure=not settings.DEBUG,
    )
    
    print("🔓 [AUTH] User logged out - both cookies cleared")
    return response