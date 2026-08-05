"""
URCV FastAPI Application Entry Point.

This is the main FastAPI application that initializes all routes,
middlewares, and dependencies.
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api.middlewares.error_handler import error_handler_middleware
from app.api.middlewares.logging import logging_middleware
from app.api.routes import health
from app.core import setup_logging
from app.core.config import settings
from app.core.logging import get_logger
from app.infrastructure.database import check_db_connection, close_db_connections

# Setup logging first
setup_logging()
logger = get_logger(__name__)


# Initialize Sentry for error tracking
if settings.SENTRY_DSN and settings.is_production:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        environment=settings.ENVIRONMENT,
    )
    logger.info("Sentry initialized")


# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info(
        "Starting URCV application",
        extra={
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG,
            "version": settings.APP_VERSION,
        }
    )
    
    # Check database connection
    db_healthy = await check_db_connection()
    if not db_healthy:
        logger.error("Database connection failed at startup")
        raise RuntimeError("Database connection failed")
    
    logger.info("Database connection verified")
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    await close_db_connections()
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    docs_url="/api/docs" if settings.is_development else None,
    redoc_url="/api/redoc" if settings.is_development else None,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    lifespan=lifespan,
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count", "X-Page-Count"],
)

# GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Custom middlewares
app.middleware("http")(logging_middleware)
app.middleware("http")(error_handler_middleware)

# Include routers
from app.api.routes import auth, resume, ats, ai
from app.api.routes import export as export_routes

app.include_router(
    health.router,
    prefix=settings.API_V1_PREFIX,
    tags=["health"]
)

app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_PREFIX}/auth",
    tags=["auth"]
)

app.include_router(
    resume.router,
    prefix=f"{settings.API_V1_PREFIX}/resumes",
    tags=["resumes"]
)

app.include_router(
    ats.router,
    prefix=f"{settings.API_V1_PREFIX}/resumes",
    tags=["ats"]
)

app.include_router(
    ai.router,
    prefix=f"{settings.API_V1_PREFIX}/resumes",
    tags=["ai"]
)

app.include_router(
    export_routes.router,
    prefix=f"{settings.API_V1_PREFIX}/resumes",
    tags=["export"]
)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "message": "URCV API",
        "version": settings.APP_VERSION,
        "docs": "/api/docs" if settings.is_development else "Documentation disabled in production",
    }


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Quick health check endpoint (non-detailed)."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.is_development,
        log_level=settings.LOG_LEVEL.lower(),
    )
