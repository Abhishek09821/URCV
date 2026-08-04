"""
Authentication dependencies for FastAPI routes.
"""
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError, InvalidTokenError
from app.core.logging import get_logger
from app.core.security import decode_token
from app.features.auth.service import AuthService
from app.infrastructure.database import get_db

logger = get_logger(__name__)


async def get_token_from_header(
    authorization: Annotated[str | None, Header()] = None
) -> str:
    """
    Extract JWT token from Authorization header.
    
    Args:
        authorization: Authorization header value
        
    Returns:
        JWT token
        
    Raises:
        AuthenticationError: If token is missing or invalid format
    """
    if not authorization:
        raise AuthenticationError("Authorization header missing")
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AuthenticationError("Invalid authorization header format")
    
    return parts[1]


async def get_current_user_id(
    token: Annotated[str, Depends(get_token_from_header)]
) -> UUID:
    """
    Get current user ID from JWT token.
    
    Args:
        token: JWT access token
        
    Returns:
        User ID
        
    Raises:
        InvalidTokenError: If token is invalid
    """
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise InvalidTokenError("Token payload missing user ID")
        
        return UUID(user_id)
    
    except JWTError as e:
        logger.warning("Invalid token", extra={"error": str(e)})
        raise InvalidTokenError("Invalid or expired token")
    except ValueError:
        raise InvalidTokenError("Invalid user ID in token")


async def get_current_user(
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Get current authenticated user.
    
    Args:
        user_id: Current user ID
        db: Database session
        
    Returns:
        User object
        
    Raises:
        AuthenticationError: If user not found or inactive
    """
    auth_service = AuthService(db)
    user = await auth_service.get_user_by_id(user_id)
    
    if not user:
        raise AuthenticationError("User not found")
    
    return user


# Type alias for dependencies
CurrentUser = Annotated[object, Depends(get_current_user)]
