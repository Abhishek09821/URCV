"""
Database session management.
Provides async session factory and connection management.
"""
from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


# Global engine instance
_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """
    Get or create the global async engine.
    
    Returns:
        AsyncEngine instance
    """
    global _engine
    
    if _engine is None:
        logger.info("Creating database engine", extra={"url": settings.DATABASE_URL})
        
        engine_kwargs: dict[str, Any] = {
            "echo": settings.DEBUG,  # Log SQL queries in debug mode
            "future": True,
            "pool_pre_ping": True,  # Verify connections before using
        }
        
        # Use NullPool for testing to avoid connection issues
        if settings.ENVIRONMENT == "testing":
            engine_kwargs["poolclass"] = NullPool
        else:
            engine_kwargs.update({
                "pool_size": 5,
                "max_overflow": 10,
                "pool_recycle": 3600,  # Recycle connections after 1 hour
            })
        
        _engine = create_async_engine(
            settings.DATABASE_URL,
            **engine_kwargs
        )
        
        logger.info("Database engine created successfully")
    
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """
    Get or create the session factory.
    
    Returns:
        Session factory for creating database sessions
    """
    global _session_factory
    
    if _session_factory is None:
        engine = get_engine()
        _session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,  # Don't expire objects after commit
            autocommit=False,
            autoflush=False,
        )
        logger.info("Session factory created")
    
    return _session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting database session in FastAPI routes.
    
    Yields:
        Database session
        
    Example:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            ...
    """
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def close_db_connections() -> None:
    """
    Close all database connections.
    Should be called on application shutdown.
    """
    global _engine, _session_factory
    
    if _engine is not None:
        logger.info("Closing database connections")
        await _engine.dispose()
        _engine = None
        _session_factory = None
        logger.info("Database connections closed")


async def check_db_connection() -> bool:
    """
    Check if database connection is healthy.
    
    Returns:
        True if connection is healthy, False otherwise
    """
    try:
        from sqlalchemy import text
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error("Database connection check failed", extra={"error": str(e)})
        return False
