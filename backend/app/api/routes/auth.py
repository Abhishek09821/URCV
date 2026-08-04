"""
Authentication API routes.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.auth import CurrentUser
from app.features.auth.schemas import (
    EmailVerificationRequest,
    PasswordChangeRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from app.features.auth.service import AuthService
from app.infrastructure.database import get_db

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Register a new user.
    
    - **email**: Valid email address
    - **password**: Minimum 8 characters with uppercase, lowercase, and digit
    - **full_name**: User's full name
    """
    auth_service = AuthService(db)
    return await auth_service.register(
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Login and receive access and refresh tokens.
    
    - **email**: User email
    - **password**: User password
    
    Returns access_token (15 min) and refresh_token (7 days).
    """
    auth_service = AuthService(db)
    return await auth_service.login(
        email=credentials.email,
        password=credentials.password
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Refresh access token using refresh token.
    
    - **refresh_token**: Valid refresh token
    
    Returns new access_token and refresh_token (token rotation).
    """
    auth_service = AuthService(db)
    return await auth_service.refresh_access_token(request.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: RefreshTokenRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Logout and revoke refresh token.
    
    Requires authentication.
    """
    auth_service = AuthService(db)
    await auth_service.logout(current_user.id, request.refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: CurrentUser):
    """
    Get current authenticated user information.
    
    Requires authentication.
    """
    return current_user


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    request: PasswordChangeRequest,
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Change user password.
    
    - **old_password**: Current password
    - **new_password**: New password (minimum 8 characters)
    
    Requires authentication.
    """
    auth_service = AuthService(db)
    await auth_service.change_password(
        user_id=current_user.id,
        old_password=request.old_password,
        new_password=request.new_password
    )
