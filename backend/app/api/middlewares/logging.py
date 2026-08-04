"""
Logging middleware for request/response logging.
"""
import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import get_logger

logger = get_logger(__name__)


async def logging_middleware(request: Request, call_next: Callable) -> Response:
    """
    Log incoming requests and outgoing responses.
    
    Args:
        request: Incoming HTTP request
        call_next: Next middleware in chain
        
    Returns:
        HTTP response
    """
    start_time = time.time()
    
    # Log request
    logger.info(
        "Incoming request",
        extra={
            "method": request.method,
            "url": str(request.url),
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        }
    )
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Log response
    logger.info(
        "Request completed",
        extra={
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "process_time_ms": round(process_time * 1000, 2),
        }
    )
    
    # Add processing time header
    response.headers["X-Process-Time"] = str(process_time)
    
    return response
