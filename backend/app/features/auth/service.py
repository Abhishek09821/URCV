"""
Authentication service - handles user registration, login, token management.
"""
from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import (
    AuthenticationError,
    InvalidCredentialsError,
    ResourceAlreadyExistsError,
    ResourceNotFoundError,
    TokenExpiredError,
)
from app.core.logging import get_logger
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    hash_token,
    validate_password_strength,
    verify_password,
)
from app.features.auth.schemas import TokenResponse, UserResponse
from app.infrastructure.database.models import RefreshToken, User

logger = get_logger(__name__)


class AuthService:
    """Authentication service."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def register(
        self,
        email: str,
        password: str,
        full_name: str
    ) -> UserResponse:
        """
        Register a new user.
        
        Args:
            email: User email
            password: Plain password
            full_name: User's full name
            
        Returns:
            Created user
            
        Raises:
            ResourceAlreadyExistsError: If email already exists
            ValidationError: If password is weak
        """
        # Check if user exists
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise ResourceAlreadyExistsError("User", email)
        
        # Validate password strength
        is_valid, error_msg = validate_password_strength(password)
        if not is_valid:
            from app.core.exceptions import ValidationError
            raise ValidationError(error_msg, field="password")
        
        # Create user
        user = User(
            email=email,
            password_hash=get_password_hash(password),
            full_name=full_name,
            is_active=True,
            is_verified=False,
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        logger.info("User registered", extra={"user_id": str(user.id), "email": email})
        
        return UserResponse.model_validate(user)
    
    async def login(self, email: str, password: str) -> TokenResponse:
        """
        Authenticate user and generate tokens.
        
        Args:
            email: User email
            password: Plain password
            
        Returns:
            Access and refresh tokens
            
        Raises:
            InvalidCredentialsError: If credentials are invalid
        """
        # Get user
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
        
        if not user or not verify_password(password, user.password_hash):
            logger.warning("Failed login attempt", extra={"email": email})
            raise InvalidCredentialsError()
        
        if not user.is_active:
            from app.core.exceptions import InactiveUserError
            raise InactiveUserError()
        
        # Update last login
        user.last_login_at = datetime.utcnow()
        await self.db.commit()
        
        # Generate tokens
        access_token = create_access_token({"sub": str(user.id), "email": user.email})
        refresh_token_str = create_refresh_token({"sub": str(user.id)})
        
        # Store refresh token
        refresh_token = RefreshToken(
            user_id=user.id,
            token_hash=hash_token(refresh_token_str),
            expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        self.db.add(refresh_token)
        await self.db.commit()
        
        logger.info("User logged in", extra={"user_id": str(user.id)})
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token_str,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    async def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """
        Generate new access token from refresh token.
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            New access and refresh tokens
            
        Raises:
            TokenExpiredError: If refresh token is invalid/expired
        """
        try:
            payload = decode_token(refresh_token)
        except Exception:
            raise TokenExpiredError("Invalid refresh token")
        
        user_id = payload.get("sub")
        if not user_id:
            raise TokenExpiredError("Invalid token payload")
        
        # Verify refresh token exists and is valid
        result = await self.db.execute(
            select(RefreshToken)
            .where(RefreshToken.user_id == UUID(user_id))
            .where(RefreshToken.revoked_at.is_(None))
            .where(RefreshToken.expires_at > datetime.utcnow())
        )
        db_token = result.scalar_one_or_none()
        
        if not db_token:
            raise TokenExpiredError("Refresh token not found or expired")
        
        # Get user
        result = await self.db.execute(
            select(User).where(User.id == UUID(user_id))
        )
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            raise AuthenticationError("User not found or inactive")
        
        # Revoke old refresh token (rotation)
        db_token.revoked_at = datetime.utcnow()
        
        # Generate new tokens
        access_token = create_access_token({"sub": str(user.id), "email": user.email})
        new_refresh_token = create_refresh_token({"sub": str(user.id)})
        
        # Store new refresh token
        new_token = RefreshToken(
            user_id=user.id,
            token_hash=hash_token(new_refresh_token),
            expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        self.db.add(new_token)
        await self.db.commit()
        
        logger.info("Token refreshed", extra={"user_id": str(user.id)})
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    async def logout(self, user_id: UUID, refresh_token: str) -> None:
        """
        Revoke refresh token.
        
        Args:
            user_id: User ID
            refresh_token: Refresh token to revoke
        """
        result = await self.db.execute(
            select(RefreshToken)
            .where(RefreshToken.user_id == user_id)
            .where(RefreshToken.revoked_at.is_(None))
        )
        db_token = result.scalar_one_or_none()
        
        if db_token:
            db_token.revoked_at = datetime.utcnow()
            await self.db.commit()
        
        logger.info("User logged out", extra={"user_id": str(user_id)})
    
    async def get_user_by_id(self, user_id: UUID) -> UserResponse:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User information
            
        Raises:
            ResourceNotFoundError: If user not found
        """
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise ResourceNotFoundError("User", str(user_id))
        
        return UserResponse.model_validate(user)
    
    async def change_password(
        self,
        user_id: UUID,
        old_password: str,
        new_password: str
    ) -> None:
        """
        Change user password.
        
        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password
            
        Raises:
            InvalidCredentialsError: If old password is wrong
            ValidationError: If new password is weak
        """
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise ResourceNotFoundError("User", str(user_id))
        
        # Verify old password
        if not verify_password(old_password, user.password_hash):
            raise InvalidCredentialsError("Current password is incorrect")
        
        # Validate new password
        is_valid, error_msg = validate_password_strength(new_password)
        if not is_valid:
            from app.core.exceptions import ValidationError
            raise ValidationError(error_msg, field="new_password")
        
        # Update password
        user.password_hash = get_password_hash(new_password)
        await self.db.commit()
        
        logger.info("Password changed", extra={"user_id": str(user_id)})
