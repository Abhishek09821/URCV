"""
Health check endpoints for monitoring application status.
"""
from datetime import datetime

from fastapi import APIRouter, status
from pydantic import BaseModel

from app.core.config import settings
from app.infrastructure.database import check_db_connection

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: datetime
    version: str
    environment: str


class DetailedHealthResponse(BaseModel):
    """Detailed health check response with component status."""
    status: str
    timestamp: datetime
    version: str
    environment: str
    components: dict[str, dict[str, str]]


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def basic_health_check() -> HealthResponse:
    """
    Basic health check endpoint.
    
    Returns:
        Basic health status
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
    )


@router.get("/health/detailed", response_model=DetailedHealthResponse, status_code=status.HTTP_200_OK)
async def detailed_health_check() -> DetailedHealthResponse:
    """
    Detailed health check endpoint with component status.
    
    Checks:
    - Database connection
    - Redis connection (TODO)
    - S3 storage (TODO)
    
    Returns:
        Detailed health status with component checks
    """
    components = {}
    overall_status = "healthy"
    
    # Check database
    db_healthy = await check_db_connection()
    components["database"] = {
        "status": "healthy" if db_healthy else "unhealthy",
        "message": "Connected" if db_healthy else "Connection failed"
    }
    
    if not db_healthy:
        overall_status = "degraded"
    
    # TODO: Check Redis
    components["cache"] = {
        "status": "unknown",
        "message": "Not implemented yet"
    }
    
    # TODO: Check S3
    components["storage"] = {
        "status": "unknown",
        "message": "Not implemented yet"
    }
    
    return DetailedHealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow(),
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
        components=components,
    )


@router.get("/health/live", status_code=status.HTTP_200_OK)
async def liveness_probe() -> dict[str, str]:
    """
    Kubernetes liveness probe.
    Returns 200 if application is running.
    """
    return {"status": "alive"}


@router.get("/health/ready", status_code=status.HTTP_200_OK)
async def readiness_probe() -> dict[str, str]:
    """
    Kubernetes readiness probe.
    Returns 200 if application is ready to serve requests.
    """
    # Check critical dependencies
    db_healthy = await check_db_connection()
    
    if not db_healthy:
        return {"status": "not ready", "reason": "database"}
    
    return {"status": "ready"}
