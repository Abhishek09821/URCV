"""
Global error handling middleware.
Catches all exceptions and returns consistent error responses.
"""
from typing import Callable

from fastapi import Request, status
from fastapi.responses import JSONResponse
from jose import JWTError
from pydantic import ValidationError

from app.core.exceptions import URCVException
from app.core.logging import get_logger

logger = get_logger(__name__)


async def error_handler_middleware(request: Request, call_next: Callable) -> JSONResponse:
    """
    Global error handler middleware.
    
    Args:
        request: Incoming HTTP request
        call_next: Next middleware in chain
        
    Returns:
        HTTP response (either success or error)
    """
    try:
        response = await call_next(request)
        return response
    
    except URCVException as exc:
        # Custom application exceptions
        logger.warning(
            "Application exception occurred",
            extra={
                "exception": exc.__class__.__name__,
                "message": exc.message,
                "status_code": exc.status_code,
                "details": exc.details,
                "url": str(request.url),
            }
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "type": exc.__class__.__name__,
                    "message": exc.message,
                    "details": exc.details,
                }
            }
        )
    
    except ValidationError as exc:
        # Pydantic validation errors
        logger.warning(
            "Validation error",
            extra={
                "errors": exc.errors(),
                "url": str(request.url),
            }
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": {
                    "type": "ValidationError",
                    "message": "Request validation failed",
                    "details": {"validation_errors": exc.errors()},
                }
            }
        )
    
    except JWTError as exc:
        # JWT authentication errors
        logger.warning(
            "JWT error",
            extra={
                "error": str(exc),
                "url": str(request.url),
            }
        )
        
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": {
                    "type": "AuthenticationError",
                    "message": "Invalid or expired token",
                    "details": {},
                }
            }
        )
    
    except Exception as exc:
        # Unexpected errors
        logger.error(
            "Unexpected error occurred",
            extra={
                "exception": exc.__class__.__name__,
                "error": str(exc),
                "url": str(request.url),
            },
            exc_info=True
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "type": "InternalServerError",
                    "message": "An unexpected error occurred",
                    "details": {} if not logger.isEnabledFor(10) else {"error": str(exc)},
                }
            }
        )
