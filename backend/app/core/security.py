"""
Security utilities for authentication and authorization.
"""
from datetime import datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(subject: str | dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """
    Create JWT access token.
    
    Args:
        subject: User ID or custom claims dict
        expires_delta: Token expiration time
        
    Returns:
        Encoded JWT token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {"exp": expire}
    
    if isinstance(subject, dict):
        to_encode.update(subject)
    else:
        to_encode.update({"sub": str(subject)})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(subject: str | dict[str, Any]) -> str:
    """
    Create JWT refresh token with longer expiration.
    
    Args:
        subject: User ID or custom claims dict
        
    Returns:
        Encoded JWT token
    """
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    expire = datetime.utcnow() + expires_delta
    
    to_encode = {"exp": expire, "type": "refresh"}
    
    if isinstance(subject, dict):
        to_encode.update(subject)
    else:
        to_encode.update({"sub": str(subject)})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> dict[str, Any]:
    """
    Decode and verify JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload
        
    Raises:
        JWTError: If token is invalid
    """
    payload = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM]
    )
    return payload


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against its hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password for storage.
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


def validate_password_strength(password: str) -> tuple[bool, str | None]:
    """
    Validate password meets minimum requirements.
    
    Args:
        password: Plain text password
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < settings.PASSWORD_MIN_LENGTH:
        return False, f"Password must be at least {settings.PASSWORD_MIN_LENGTH} characters"
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    
    if not (has_upper and has_lower and has_digit):
        return False, "Password must contain uppercase, lowercase, and digit"
    
    return True, None


def hash_token(token: str) -> str:
    """
    Hash a token for secure storage (e.g., refresh tokens).
    
    Args:
        token: Token to hash
        
    Returns:
        Hashed token
    """
    return pwd_context.hash(token)


def verify_token_hash(token: str, token_hash: str) -> bool:
    """
    Verify a token against its hash.
    
    Args:
        token: Plain token
        token_hash: Hashed token
        
    Returns:
        True if token matches, False otherwise
    """
    return pwd_context.verify(token, token_hash)
